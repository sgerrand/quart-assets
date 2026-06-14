from webassets.bundle import Bundle  # noqa: F401

from .extension import (
    assets,
    AsyncAssetsExtension,
    Jinja2Filter,
    QuartAssets,
    QuartConfigStorage,
    QuartResolver,
)

__version__ = "0.1.6"  # x-release-please-version

__all__ = (
    "assets",
    "Bundle",
    "QuartAssets",
    "QuartConfigStorage",
    "QuartResolver",
    "Jinja2Filter",
    "AsyncAssetsExtension",
)
