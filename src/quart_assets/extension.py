"""Integration of the ``webassets`` library with Quart."""

import asyncio
import inspect
import logging
from os import path
from types import ModuleType
from typing import Any

import click
from quart import has_app_context, has_request_context, url_for
from quart.app import Quart
from quart.cli import pass_script_info, ScriptInfo
from quart.globals import app_ctx, request_ctx
from quart.templating import render_template_string
from webassets.env import BaseEnvironment, ConfigStorage, env_options, Resolver
from webassets.ext.jinja2 import AssetsExtension
from webassets.filter import Filter, register_filter
from webassets.loaders import PythonLoader, YAMLLoader
from webassets.script import CommandLineEnvironment


def get_static_folder(app_or_blueprint: Any) -> str:
    """Return the static folder of the given Quart app
    instance, or module/blueprint.
    """
    if not app_or_blueprint.has_static_folder:
        raise TypeError(f"The referenced blueprint {app_or_blueprint} has no static folder.")
    return app_or_blueprint.static_folder


class AsyncAssetsExtension(AssetsExtension):
    """Async-aware webassets Jinja2 extension for Quart's async Jinja environment."""

    def _render_assets(
        self, filter: Any, output: Any, dbg: Any, depends: Any, files: Any, caller: Any = None
    ) -> Any:
        if self.environment.is_async:
            return self._render_assets_async(filter, output, dbg, depends, files, caller)
        return self._render_assets_sync(filter, output, dbg, depends, files, caller)

    def _build_bundle(
        self, filter: Any, output: Any, dbg: Any, depends: Any, files: Any
    ) -> tuple[Any, Any]:
        env = self.environment.assets_environment  # ty: ignore[unresolved-attribute]
        if env is None:
            raise RuntimeError("No assets environment configured in Jinja2 environment")

        bundle_kwargs = {
            "output": output,
            "filters": filter,
            "debug": dbg,
            "depends": depends,
        }
        bundle = self.BundleClass(*self.resolve_contents(files, env), **bundle_kwargs)

        with bundle.bind(env):
            urls = bundle.urls(calculate_sri=True)
        return bundle, urls

    def _render_assets_sync(
        self, filter: Any, output: Any, dbg: Any, depends: Any, files: Any, caller: Any
    ) -> str:
        bundle, urls = self._build_bundle(filter, output, dbg, depends, files)
        parts: list[str] = []
        for entry in urls:
            if isinstance(entry, dict):
                parts.append(caller(entry["uri"], entry.get("sri", None), bundle.extra))
            else:
                parts.append(caller(entry, None, bundle.extra))
        return "".join(parts)

    async def _render_assets_async(
        self, filter: Any, output: Any, dbg: Any, depends: Any, files: Any, caller: Any
    ) -> str:
        bundle, urls = self._build_bundle(filter, output, dbg, depends, files)
        parts: list[str] = []
        for entry in urls:
            if isinstance(entry, dict):
                caller_result = caller(entry["uri"], entry.get("sri", None), bundle.extra)
            else:
                caller_result = caller(entry, None, bundle.extra)
            if inspect.iscoroutine(caller_result):
                caller_result = await caller_result
            parts.append(caller_result)
        return "".join(parts)


class Jinja2Filter(Filter):
    """Compiles all source files as Jinja2 templates using Quart contexts."""

    name: str = "jinja2"
    max_debug_level = None

    def __init__(self, context: dict[str, Any] | None = None) -> None:
        super().__init__()
        self.context = context or {}

    def input(self, _in: Any, out: Any, **kw: Any) -> None:
        out.write(render_template_string(_in.read(), **self.context))


class QuartConfigStorage(ConfigStorage):
    """Uses the config object of a Quart app as the backend: either the app
    instance bound to the extension directly, or the current Quart app on
    the stack. Also provides per-application defaults for some values.
    """

    def __init__(self, *a: Any, **kw: Any) -> None:
        self._defaults: dict[str, Any] = {}
        ConfigStorage.__init__(self, *a, **kw)

    def _transform_key(self, key: str) -> str:
        if key.lower() in env_options:
            return f"ASSETS_{key.upper()}"

        return key.upper()

    def setdefault(self, key: str, value: Any) -> None:
        """We may not always be connected to an app, but we still need
        to provide a way to the base environment to set its defaults.
        """
        try:
            super().setdefault(key, value)
        except RuntimeError:
            self._defaults[key] = value

    def __contains__(self, key: str) -> bool:
        return self._transform_key(key) in self.env._app.config

    def __getitem__(self, key: str) -> Any:
        value = self._get_deprecated(key)
        if value is not None:
            return value

        # First try the current app's config
        public_key = self._transform_key(key)
        if self.env._app:
            if public_key in self.env._app.config:
                return self.env._app.config[public_key]

        # Try a non-app specific default value
        if key in self._defaults:
            return self._defaults.__getitem__(key)

        # We've run out of options
        raise KeyError()

    def __setitem__(self, key: str, value: Any) -> None:
        if not self._set_deprecated(key, value):
            self.env._app.config[self._transform_key(key)] = value

    def __delitem__(self, key: str) -> None:
        del self.env._app.config[self._transform_key(key)]


class QuartResolver(Resolver):
    """Adds support for Quart blueprints.

    This resolver is designed to use the Quart staticfile system to
    locate files, by looking at directory prefixes. (``foo/bar.png``
    looks in the static folder of the ``foo`` blueprint. ``url_for``
    is used to generate urls to these files.)

    This default behaviour changes when you start setting certain
    standard *webassets* path and url configuration values:

    If a :attr:`Environment.directory` is set, output files will
    always be written there, while source files still use the Quart
    system.

    If a :attr:`Environment.load_path` is set, it is used to look
    up source files, replacing the Quart system. Blueprint prefixes
    are no longer resolved.
    """

    def split_prefix(self, ctx: Any, item: str) -> tuple[str, str, str]:
        """Split a blueprint-prefixed asset path.

        Returns ``(directory, relative_path, endpoint)``. If ``item`` has a
        ``blueprint_name/...`` prefix that matches a registered blueprint with
        a static folder, the blueprint's static folder and endpoint are used.
        Otherwise the app's static folder is used and ``item`` is returned
        unchanged.

        Raises:
            ValueError: If ``item`` is empty or no app context is available.
            TypeError: If the matched blueprint, or the app, has no static folder.
        """
        if not item:
            raise ValueError("Asset item cannot be empty")

        app = ctx._app
        if app is None:
            raise ValueError("No app context available")

        if "/" in item:
            blueprint_name, name = item.split("/", 1)
            if blueprint_name and name and blueprint_name in app.blueprints:
                try:
                    directory = get_static_folder(app.blueprints[blueprint_name])
                except TypeError as e:
                    raise TypeError(f"Blueprint '{blueprint_name}' has no static folder") from e
                return directory, name, f"{blueprint_name}.static"

        try:
            directory = get_static_folder(app)
        except TypeError as e:
            raise TypeError("App has no static folder configured") from e
        return directory, item, "static"

    def use_webassets_system_for_output(self, ctx: Any) -> bool:
        return ctx.config.get("directory") is not None or ctx.config.get("url") is not None

    def use_webassets_system_for_sources(self, ctx: Any) -> bool:
        return bool(ctx.load_path)

    def search_for_source(self, ctx: Any, item: str) -> Any:
        if self.use_webassets_system_for_sources(ctx):
            return Resolver.search_for_source(self, ctx, item)

        directory, item, _ = self.split_prefix(ctx, item)
        try:
            return self.consider_single_directory(directory, item)
        except IOError:
            # Return the would-be path so webassets can report a useful
            # "missing source" error later instead of an opaque IOError here.
            return path.normpath(path.join(directory, item))

    def resolve_output_to_path(self, ctx: Any, target: str, bundle: Any) -> Any:
        if self.use_webassets_system_for_output(ctx):
            return Resolver.resolve_output_to_path(self, ctx, target, bundle)

        directory, rel_path, _ = self.split_prefix(ctx, target)
        return path.normpath(path.join(directory, rel_path))

    def resolve_source_to_url(self, ctx: Any, filepath: str, item: str) -> str:
        if self.use_webassets_system_for_sources(ctx):
            return super().resolve_source_to_url(ctx, filepath, item)
        return self.convert_item_to_quart_url(ctx, item, filepath)

    def resolve_output_to_url(self, ctx: Any, target: str) -> str:
        if self.use_webassets_system_for_output(ctx):
            return Resolver.resolve_output_to_url(self, ctx, target)
        return self.convert_item_to_quart_url(ctx, target)

    def convert_item_to_quart_url(self, ctx: Any, item: str, filepath: str | None = None) -> str:
        """Build a Quart URL for an asset reference.

        Resolves blueprint prefixes via :meth:`split_prefix` and asks the
        app's URL map to construct the URL for the matching static endpoint.
        Works both inside a request context (via :func:`quart.url_for`) and
        outside one (e.g. during ``quart assets build``), correctly honouring
        blueprint ``static_url_path`` values and any custom URL routing.

        If ``filepath`` is provided it overrides the relative path returned by
        :meth:`split_prefix`; this is needed when ``item`` is a glob that was
        resolved to multiple files.
        """
        directory, rel_path, endpoint = self.split_prefix(ctx, item)

        if filepath is not None:
            filename = path.relpath(filepath, directory)
        else:
            filename = rel_path
        filename = filename.replace("\\", "/")

        if has_request_context():
            url = url_for(endpoint, filename=filename)
        else:
            # `url_for` outside a request context needs SERVER_NAME; bind the
            # adapter directly so the URL map still resolves the static rules.
            app = ctx.environment._app
            server_name = app.config.get("SERVER_NAME") or ""
            url_adapter = app.url_map.bind(server_name, url_scheme="http")
            url = url_adapter.build(endpoint, {"filename": filename}, force_external=False)

        # Scheme is unknown during build; emit scheme-relative URLs.
        if url:
            url = url.removeprefix("http:")
        return url


class QuartAssets(BaseEnvironment):
    """This object is used to hold a collection of bundles and configuration.

    If initialized with a Quart app instance then a webassets Jinja2 extension
    is automatically registered.
    """

    config_storage_class: Any = QuartConfigStorage
    resolver_class = QuartResolver

    def __init__(self, app: Quart | None = None) -> None:
        self.app = app
        super().__init__()
        if app:
            self.init_app(app)

    @property
    def _app(self) -> Quart:
        """The application object; this is either the app that has been bound
        to, or the current application.
        """
        if self.app is not None:
            return self.app

        if has_request_context():
            return request_ctx.app

        if has_app_context():
            return app_ctx.app

        raise RuntimeError(
            "Assets instance not bound to an application, "
            + "and no application in current context"
        )

    def set_directory(self, directory: str) -> None:
        self.config["directory"] = directory

    def get_directory(self) -> str:
        if self.config.get("directory") is not None:
            return self.config["directory"]
        return get_static_folder(self._app)

    directory = property(
        get_directory,
        set_directory,
        doc="""The base directory to which all paths will be relative to.
    """,
    )

    def set_url(self, url: str) -> None:
        self.config["url"] = url

    def get_url(self) -> str | None:
        if self.config.get("url") is not None:
            return self.config["url"]
        return self._app.static_url_path

    url = property(
        get_url,
        set_url,
        doc="""The base url to which all static urls will be relative to.""",
    )

    def init_app(self, app: Quart) -> None:
        # Use our custom async-aware extension instead of the default webassets
        # extension
        app.jinja_env.add_extension(AsyncAssetsExtension)
        app.jinja_env.assets_environment = self  # ty: ignore[unresolved-attribute]

    def from_yaml(self, path: str) -> None:
        """Register bundles from a YAML configuration file."""
        self.register(YAMLLoader(path).load_bundles())

    def from_module(self, path: str | ModuleType) -> None:
        """Register bundles from a Python module."""
        self.register(PythonLoader(path).load_bundles())


# Override webassets' default jinja2 filter so it renders with Quart's
# template context.
register_filter(Jinja2Filter)


def _webassets_cmd(cmd: str, info: ScriptInfo) -> None:
    """Helper to run a webassets command."""
    app = info.load_app()

    if not hasattr(app.jinja_env, "assets_environment"):
        raise RuntimeError(
            "No assets environment found. Make sure you've "
            + "initialized QuartAssets with your app."
        )

    logger = logging.getLogger("webassets")
    if not logger.handlers:
        logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)

    async def _run_with_app_context() -> None:
        async with app.app_context():  # ty: ignore[invalid-context-manager]
            cmdenv = CommandLineEnvironment(
                app.jinja_env.assets_environment,  # ty: ignore[unresolved-attribute]
                logger,
            )
            getattr(cmdenv, cmd)()

    asyncio.run(_run_with_app_context())


@click.group()
def assets() -> None:
    """Quart Assets commands."""


@assets.command()
@pass_script_info
def build(info: ScriptInfo) -> None:
    """Build bundles."""
    _webassets_cmd("build", info)


@assets.command()
@pass_script_info
def clean(info: ScriptInfo) -> None:
    """Clean bundles."""
    _webassets_cmd("clean", info)


@assets.command()
@pass_script_info
def watch(info: ScriptInfo) -> None:
    """Watch bundles for file changes."""
    _webassets_cmd("watch", info)
