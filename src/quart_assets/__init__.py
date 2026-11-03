from webassets.bundle import Bundle  # noqa: F401

from .extension import (
    assets,
    AsyncAssetsExtension,
    Jinja2Filter,
    QuartAssets,
    QuartConfigStorage,
    QuartResolver,
)

__version__ = "1.0.0"  # x-release-please-version

__all__ = (
    "assets",
    "Bundle",
    "QuartAssets",
    "QuartConfigStorage",
    "QuartResolver",
    "Jinja2Filter",
    "AsyncAssetsExtension",
)
