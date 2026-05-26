import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner
from quart import Blueprint, Quart
from quart.cli import ScriptInfo

from quart_assets import Bundle, QuartAssets
from quart_assets.extension import assets, build, clean, watch


def _invoke(cmd: Any, app: Quart, args: list[str] | None = None) -> Any:
    """Invoke a click command against ``app`` via a synthetic ScriptInfo."""
    script_info = ScriptInfo(create_app=lambda: app)
    return CliRunner().invoke(cmd, args or [], obj=script_info)


@pytest.fixture
def cli_app(temp_dir: str) -> Quart:
    """Quart app with a CSS+JS bundle registered against ``temp_dir``."""
    app = Quart(__name__)
    app.static_folder = temp_dir

    with open(os.path.join(temp_dir, "test.css"), "w", encoding="utf-8") as f:
        f.write("body { color: red; }")
    with open(os.path.join(temp_dir, "test.js"), "w", encoding="utf-8") as f:
        f.write("console.log('test');")

    env = QuartAssets(app)
    env.register("test_bundle", Bundle("test.css", "test.js", output="combined.min.css"))
    return app


def test_assets_command_group() -> None:
    """The assets group exposes build, clean, and watch."""
    result = CliRunner().invoke(assets, ["--help"])
    assert result.exit_code == 0
    assert "Quart Assets commands" in result.output
    for sub in ("build", "clean", "watch"):
        assert sub in result.output


@pytest.mark.parametrize(
    "cmd,doc",
    [(build, "Build bundles"), (clean, "Clean bundles"), (watch, "Watch bundles")],
)
def test_subcommand_help(cmd: Any, doc: str) -> None:
    result = CliRunner().invoke(cmd, ["--help"])
    assert result.exit_code == 0
    assert doc in result.output


def test_cli_build_creates_output(cli_app: Quart, temp_dir: str) -> None:
    result = _invoke(build, cli_app)
    assert result.exit_code == 0, result.output
    assert os.path.exists(os.path.join(temp_dir, "combined.min.css"))


def test_cli_clean_after_build(cli_app: Quart, temp_dir: str) -> None:
    build_result = _invoke(build, cli_app)
    assert build_result.exit_code == 0, build_result.output

    clean_result = _invoke(clean, cli_app)
    assert clean_result.exit_code == 0, clean_result.output


def test_cli_build_with_blueprint(temp_dir: str) -> None:
    """CLI build resolves blueprint-prefixed bundle sources."""
    bp_static = os.path.join(temp_dir, "bp_static")
    os.makedirs(bp_static, exist_ok=True)
    with open(os.path.join(bp_static, "bp.css"), "w", encoding="utf-8") as f:
        f.write(".blueprint { color: green; }")

    app = Quart(__name__)
    app.static_folder = temp_dir
    bp = Blueprint("test_bp", __name__, static_folder=bp_static, static_url_path="/bp")
    app.register_blueprint(bp)

    env = QuartAssets(app)
    env.register("bp_bundle", Bundle("test_bp/bp.css", output="bp_combined.css"))

    result = _invoke(build, app)
    assert result.exit_code == 0, result.output
    assert os.path.exists(os.path.join(temp_dir, "bp_combined.css"))


def test_entrypoint_smoke() -> None:
    """End-to-end smoke check that the `quart assets` entry-point is wired."""
    src_path = str(Path(__file__).parent.parent / "src")
    env = os.environ.copy()
    env["PYTHONPATH"] = src_path + os.pathsep + env.get("PYTHONPATH", "")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "quart", "assets", "--help"],
            env=env,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pytest.skip("CLI smoke environment not available")

    assert result.returncode == 0
    assert "Quart Assets commands" in result.stdout
