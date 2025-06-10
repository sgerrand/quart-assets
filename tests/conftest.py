import asyncio
import shutil
import tempfile
from typing import Any, Callable, Generator

import pytest
from quart import Quart

from quart_assets import QuartAssets
from tests.helpers import new_blueprint


@pytest.fixture
def app() -> Quart:
    app = Quart(__name__, static_url_path="/app_static")
    bp = new_blueprint("bp", static_url_path="/bp_static", static_folder="static")
    app.register_blueprint(bp)
    return app


@pytest.fixture
def env(app: Quart) -> QuartAssets:
    env = QuartAssets(app)
    return env


@pytest.fixture
def no_app_env() -> QuartAssets:
    return QuartAssets()


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    temp = tempfile.mkdtemp()
    yield temp
    shutil.rmtree(temp, ignore_errors=True)


def run_with_context(app: Quart, func: Callable[[], Any]) -> Any:
    """Helper to run a function within an async request context."""

    async def _run() -> Any:
        async with app.test_request_context("/"):
            result = func()
            # If result is a coroutine, await it
            if hasattr(result, "__await__"):
                return await result
            return result

    return asyncio.run(_run())


def run_with_context_async(app: Quart, func: Callable[[], Any]) -> Any:
    """Helper to run an async function within an async request context."""

    async def _run() -> Any:
        async with app.test_request_context("/"):
            return await func()

    return asyncio.run(_run())
