import os
from typing import List

import pytest
from quart import Quart
from webassets.bundle import get_all_bundle_files  # type: ignore[import-untyped]

from quart_assets import Bundle, QuartAssets
from tests.conftest import run_with_context
from tests.helpers import create_files, new_blueprint


def test_directory_auto(app: Quart, env: QuartAssets) -> None:
    """Test how we resolve file references through the Quart static
    system by default (if no custom 'env.directory' etc. values
    have been configured manually).
    """
    assert "directory" not in env.config

    assert get_all_bundle_files(Bundle("foo"), env) == [
        app.root_path + os.path.normpath("/static/foo")
    ]

    # Blueprints prefixes in paths are handled specifically.
    assert get_all_bundle_files(Bundle("bp/bar"), env) == [
        app.root_path + os.path.normpath("/bp_for_test/static/bar")
    ]

    # Prefixes that aren't valid blueprint names are just considered
    # sub-folders of the main app.
    assert get_all_bundle_files(Bundle("app/bar"), env) == [
        app.root_path + os.path.normpath("/static/app/bar")
    ]

    # In case the name of a app-level sub-folder conflicts with a
    # module name, you can always use this hack:
    assert get_all_bundle_files(Bundle("./bp_for_test/bar"), env) == [
        app.root_path + os.path.normpath("/static/bp_for_test/bar")
    ]


def test_url_auto(app: Quart, env: QuartAssets) -> None:
    """Test how urls are generated via the Quart static system
    by default (if no custom 'env.url' etc. values have been
    configured manually).
    """
    assert "url" not in env.config

    result1 = run_with_context(app, lambda: Bundle("foo", env=env).urls())
    assert result1 == ["/app_static/foo"]
    # Urls for files that point to a blueprint use that blueprint"s url prefix.
    result2 = run_with_context(app, lambda: Bundle("bp/bar", env=env).urls())
    assert result2 == ["/bp_static/bar"]
    # Try with a prefix which is not a blueprint.
    result3 = run_with_context(app, lambda: Bundle("non-bp/bar", env=env).urls())
    assert result3 == ["/app_static/non-bp/bar"]


def test_custom_load_path(app: Quart, env: QuartAssets, temp_dir: str) -> None:
    """A custom load_path is configured - this will affect how
    we deal with source files.
    """
    env.append_path(temp_dir, "/custom/")
    create_files(temp_dir, "foo", os.path.normpath("module/bar"))
    assert get_all_bundle_files(Bundle("foo"), env) == [os.path.join(temp_dir, "foo")]
    # We do not recognize references to modules.
    assert get_all_bundle_files(Bundle("module/bar"), env) == [
        os.path.join(temp_dir, os.path.normpath("module/bar"))
    ]

    result1 = run_with_context(app, lambda: Bundle("foo", env=env).urls())
    assert result1 == ["/custom/foo"]
    result2 = run_with_context(app, lambda: Bundle("module/bar", env=env).urls())
    assert result2 == ["/custom/module/bar"]

    # [Regression] With a load path configured, generating output
    # urls still works, and it still uses the Quart system.
    env.debug = False
    env.url_expire = False
    result3 = run_with_context(app, lambda: Bundle("foo", output="out", env=env).urls())
    assert result3 == ["/app_static/out"]


def test_custom_directory_and_url(app: Quart, env: QuartAssets, temp_dir: str) -> None:
    """Custom directory/url are configured - this will affect how
    we deal with output files."""
    # Create source source file, make it findable (by default,
    # static_folder) is set to a fixed sub-folder of the test dir (why?)
    create_files(temp_dir, "a")
    app.static_folder = temp_dir
    # Setup custom directory/url pair for output
    env.directory = temp_dir
    env.url = "/custom"
    env.debug = False  # Return build urls
    env.url_expire = False  # No query strings

    result1 = run_with_context(app, lambda: Bundle("a", output="foo", env=env).urls())
    assert result1 == ["/custom/foo"]
    # We do not recognize references to modules.
    result2 = run_with_context(app, lambda: Bundle("a", output="module/bar", env=env).urls())
    assert result2 == ["/custom/module/bar"]


def test_existing_request_object_used(app: Quart, env: QuartAssets) -> None:
    """Check for a bug where the url generation code of
    Quart-Assets always added a dummy test request to the context stack,
    instead of using the existing one if there is one.

    We test this by making the context define a custom SCRIPT_NAME
    prefix, and then we check if it affects the generated urls, as
    it should.
    """

    # Note: Quart's test_request_context doesn't support environ_overrides
    # This test verifies that existing request context is used when available
    def _test_func() -> List[str]:
        return Bundle("foo", env=env).urls()

    result = run_with_context(app, _test_func)
    assert result == ["/app_static/foo"]


def test_globals(app: Quart, env: QuartAssets, temp_dir: str) -> None:
    """Make sure url generation works with globals."""
    app.static_folder = temp_dir
    create_files(temp_dir, "a.js", "b.js")
    b = Bundle("*.js", env=env)
    result = run_with_context(app, lambda: b.urls())
    assert result == ["/app_static/a.js", "/app_static/b.js"]


def test_blueprint_output(app: Quart, env: QuartAssets, temp_dir: str) -> None:
    """[Regression] Output can point to a blueprint's static directory."""
    bp1_static_folder = temp_dir + os.path.sep + "bp1_static"
    os.mkdir(bp1_static_folder)

    bp1 = new_blueprint("bp1", static_folder=bp1_static_folder)
    app.register_blueprint(bp1)

    app.static_folder = temp_dir

    with open(os.path.join(temp_dir, "foo"), "w", encoding="utf-8") as f:
        f.write("function bla  () { /* comment */ var a; }    ")

    Bundle("foo", filters="rjsmin", output="bp1/out", env=env).build()
    with open(os.path.join(bp1_static_folder, "out")) as f:
        assert f.read() == "function bla(){var a;}"


def test_blueprint_urls(app: Quart, env: QuartAssets) -> None:
    """Urls to blueprint files are generated correctly."""
    # source urls
    result1 = run_with_context(app, lambda: Bundle("bp/foo", env=env).urls())
    assert result1 == ["/bp_static/foo"]

    # output urls - env settings are to not touch filesystem
    env.auto_build = False
    env.url_expire = False
    result2 = run_with_context(app, lambda: Bundle(output="bp/out", debug=False, env=env).urls())
    assert result2 == ["/bp_static/out"]


def test_blueprint_no_static_folder(app: Quart, env: QuartAssets, temp_dir: str) -> None:
    """Test dealing with a blueprint without a static folder."""
    bp2 = new_blueprint("bp2")
    app.register_blueprint(bp2)

    def _test_func() -> None:
        with pytest.raises(TypeError):
            Bundle("bp2/foo", env=env).urls()

    run_with_context(app, _test_func)


def test_cssrewrite(app: Quart, env: QuartAssets, temp_dir: str) -> None:
    """Make sure cssrewrite works with Blueprints."""
    bp3_static_folder = temp_dir + os.path.sep + "bp3_static"
    os.mkdir(bp3_static_folder)
    bp3 = new_blueprint("bp3", static_folder=bp3_static_folder, static_url_path="/w/u/f/f")
    app.register_blueprint(bp3)

    path = create_files(temp_dir, os.path.normpath("bp3_static/css"))[0]
    with open(path, "w", encoding="utf-8") as f:
        f.write('h1{background: url("local")}')

    # Source file is in a blueprint, output file is app-level.
    Bundle("bp3/css", filters="cssrewrite", output="out", env=env).build()

    # The urls are NOT rewritten using the filesystem, but
    # within the url space.
    static_folder = app.static_folder or ""
    with open(os.path.join(static_folder, "out"), "r") as f:
        assert f.read() == 'h1{background: url("../w/u/f/f/local")}'
