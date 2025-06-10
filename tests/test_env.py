import os
import types

from quart import Quart

from quart_assets import Bundle, QuartAssets
from tests.conftest import run_with_context_async


def test_assets_tag(app: Quart, env: QuartAssets) -> None:
    env.register("test", "file1", "file2")
    template = app.jinja_env.from_string("{% assets 'test' %}{{ASSET_URL}};{% endassets %}")
    result = run_with_context_async(app, lambda: template.render_async())
    assert result == "/app_static/file1;/app_static/file2;"


def test_from_module(app: Quart, env: QuartAssets) -> None:
    module = types.ModuleType("test")
    setattr(module, "pytest", Bundle("py_file1", "py_file2"))
    env.from_module(module)
    template = app.jinja_env.from_string('{% assets "pytest" %}{{ASSET_URL}};{% endassets %}')
    result = run_with_context_async(app, lambda: template.render_async())
    assert result == "/app_static/py_file1;/app_static/py_file2;"


def test_from_yaml(app: Quart, env: QuartAssets) -> None:
    with open("test.yaml", "w", encoding="utf-8") as f:
        f.write(
            """
        yaml_test:
            contents:
                - yaml_file1
                - yaml_file2
        """
        )
    try:
        env.from_yaml("test.yaml")
        template = app.jinja_env.from_string(
            '{% assets "yaml_test" %}{{ASSET_URL}};{% endassets %}'
        )
        result = run_with_context_async(app, lambda: template.render_async())
        assert result == "/app_static/yaml_file1;/app_static/yaml_file2;"
    finally:
        os.remove("test.yaml")
