import pytest
from quart import Quart

from quart_assets import QuartAssets
from tests.conftest import run_with_context


def test_env_set(app: Quart, env: QuartAssets) -> None:
    env.url = "https://github.com/sgerrand/quart-assets"
    assert app.config["ASSETS_URL"] == "https://github.com/sgerrand/quart-assets"


def test_env_get(app: Quart, env: QuartAssets) -> None:
    app.config["ASSETS_URL"] = "https://github.com/sgerrand/quart-assets"
    assert env.url == "https://github.com/sgerrand/quart-assets"


def test_env_config(app: Quart, env: QuartAssets) -> None:
    app.config["LESS_PATH"] = "/usr/bin/less"
    assert env.config["LESS_PATH"] == "/usr/bin/less"

    with pytest.raises(KeyError):
        _ = env.config["do_not_exist"]

    assert env.config.get("do_not_exist") is None


def test_no_app_env_set(no_app_env: QuartAssets) -> None:
    with pytest.raises(RuntimeError):
        no_app_env.debug = True


def test_no_app_env_get(no_app_env: QuartAssets) -> None:
    with pytest.raises(RuntimeError):
        no_app_env.config.get("debug")


def test_no_app_env_config(app: Quart, no_app_env: QuartAssets) -> None:
    no_app_env.config.setdefault("foo", "bar")
    result = run_with_context(app, lambda: no_app_env.config["foo"])
    assert result == "bar"


def test_config_isolation_within_apps(no_app_env: QuartAssets) -> None:
    no_app_env.config.setdefault("foo", "bar")

    app1 = Quart(__name__)
    result1 = run_with_context(app1, lambda: no_app_env.config["foo"])
    assert result1 == "bar"

    run_with_context(app1, lambda: no_app_env.config.__setitem__("foo", "qux"))
    result2 = run_with_context(app1, lambda: no_app_env.config["foo"])
    assert result2 == "qux"

    app2 = Quart(__name__)
    result3 = run_with_context(app2, lambda: no_app_env.config["foo"])
    assert result3 == "bar"
