from __future__ import print_function

try:
    from quart.globals import app_ctx, request_ctx
except ImportError:
    from quart import _app_ctx_stack, _request_ctx_stack  # type: ignore

    request_ctx = _request_ctx_stack.top
    app_ctx = _app_ctx_stack.top

from webassets import Bundle  # type: ignore[import-untyped]  # noqa F401

from .extension import (
    assets,
    AsyncAssetsExtension,
    Jinja2Filter,
    QuartAssets,
    QuartConfigStorage,
    QuartResolver,
)

__version__ = "0.1.1.post1"

__all__ = (
    "assets",
    "Bundle",
    "QuartAssets",
    "QuartConfigStorage",
    "QuartResolver",
    "Jinja2Filter",
    "AsyncAssetsExtension",
)
