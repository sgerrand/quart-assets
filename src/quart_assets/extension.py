"""Integration of the ``webassets`` library with Quart."""

import asyncio
import inspect
import logging
from os import path
from typing import Any, Dict, Optional, Tuple, Union

from quart import has_app_context, has_request_context
from quart.app import Quart
from quart.cli import pass_script_info, ScriptInfo
from quart.globals import app_ctx, request_ctx
from quart.templating import render_template_string
from webassets.env import (  # type: ignore[import-untyped]
    BaseEnvironment,
    ConfigStorage,
    env_options,
    Resolver,
)
from webassets.ext.jinja2 import AssetsExtension  # type: ignore[import-untyped]
from webassets.filter import Filter, register_filter  # type: ignore[import-untyped]
from webassets.loaders import PythonLoader, YAMLLoader  # type: ignore[import-untyped]
from webassets.script import CommandLineEnvironment  # type: ignore[import-untyped]


def get_static_folder(app_or_blueprint: Any) -> str:
    """Return the static folder of the given Quart app
    instance, or module/blueprint.
    """
    if not app_or_blueprint.has_static_folder:
        raise TypeError(f"The referenced blueprint {app_or_blueprint} has no static " "folder.")
    return app_or_blueprint.static_folder


class AsyncAssetsExtension(AssetsExtension):  # type: ignore[misc]
    """An async-aware version of the webassets Jinja2 extension that supports async coroutines."""

    def _render_assets(
        self, filter: Any, output: Any, dbg: Any, depends: Any, files: Any, caller: Any = None
    ) -> str:
        env = self.environment.assets_environment  # pyright: ignore[reportAttributeAccessIssue]
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

        result = ""
        for entry in urls:
            if isinstance(entry, dict):
                caller_result = caller(entry["uri"], entry.get("sri", None), bundle.extra)
            else:
                caller_result = caller(entry, None, bundle.extra)

            caller_result = self._handle_async_caller_result(caller_result)
            result += caller_result
        return result

    def _handle_async_caller_result(self, caller_result: Any) -> str:
        """Handle potentially async caller results from Jinja2 template rendering.

        Args:
            caller_result: The result from calling the Jinja2 macro, which may be
                          a string or a coroutine.

        Returns:
            The rendered string result.

        Raises:
            RuntimeError: If async handling fails.
        """
        if not inspect.iscoroutine(caller_result):
            return caller_result

        import concurrent.futures

        def run_coroutine_in_thread() -> str:
            """Run the coroutine in a separate thread with a new event loop."""
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(caller_result)
            finally:
                try:
                    loop.close()
                except Exception:
                    pass
                asyncio.set_event_loop(None)

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(run_coroutine_in_thread)
                try:
                    return future.result(timeout=10.0)
                except concurrent.futures.TimeoutError:
                    raise RuntimeError("Timeout waiting for async template rendering")

        except Exception as exc:
            if inspect.iscoroutine(caller_result):
                try:
                    caller_result.close()
                except Exception:
                    pass

            raise RuntimeError(f"Failed to render async template content: {exc}") from exc


__all__ = ["Jinja2Filter"]


class Jinja2Filter(Filter):  # type: ignore[misc]
    """Compiles all source files as Jinja2 templates using Quart contexts."""

    name = "jinja2"
    max_debug_level = None

    def __init__(self, context: Optional[Dict[str, Any]] = None) -> None:
        super().__init__()
        self.context = context or {}

    def input(self, _in: Any, out: Any, **kw: Any) -> None:
        out.write(render_template_string(_in.read(), **self.context))


class QuartConfigStorage(ConfigStorage):  # type: ignore[misc]
    """Uses the config object of a Quart app as the backend: either the app
    instance bound to the extension directly, or the current Quart app on
    the stack. Also provides per-application defaults for some values.
    """

    def __init__(self, *a: Any, **kw: Any) -> None:
        self._defaults: Dict[str, Any] = {}
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
        if value:
            return value

        # First try the current app's config
        public_key = self._transform_key(key)
        if self.env._app:
            if public_key in self.env._app.config:
                return self.env._app.config[public_key]

        # Try a non-app specific default value
        if key in self._defaults:
            return self._defaults.__getitem__(key)

        # Finally try to use a default based on the current app
        deffunc = getattr(self, f"_app_default_{key}", None)
        if deffunc and callable(deffunc):
            return deffunc()

        # We've run out of options
        raise KeyError()

    def __setitem__(self, key: str, value: Any) -> None:
        if not self._set_deprecated(key, value):
            self.env._app.config[self._transform_key(key)] = value

    def __delitem__(self, key: str) -> None:
        del self.env._app.config[self._transform_key(key)]


class QuartResolver(Resolver):  # type: ignore[misc]
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

    def split_prefix(self, ctx: Any, item: str) -> Tuple[str, str, str]:
        """See if ``item`` has blueprint prefix, return (directory, rel_path, endpoint).

        Args:
            ctx: The webassets environment context
            item: Asset path that may contain blueprint prefix (e.g., "blueprint_name/file.css")

        Returns:
            Tuple of (directory, relative_path, endpoint)

        Raises:
            TypeError: If app context is invalid or blueprint lacks static folder
            ValueError: If item is empty or invalid
        """
        if not item:
            raise ValueError("Asset item cannot be empty")

        app = ctx._app
        if app is None:
            raise ValueError("No app context available")

        directory = ""
        endpoint = ""
        original_item = item

        try:
            if hasattr(app, "blueprints") and "/" in item:
                try:
                    blueprint_name, name = item.split("/", 1)
                    if not blueprint_name or not name:
                        raise ValueError(f"Invalid blueprint prefix format in '{item}'")

                    if blueprint_name in app.blueprints:
                        blueprint = app.blueprints[blueprint_name]
                        try:
                            directory = get_static_folder(blueprint)
                            endpoint = f"{blueprint_name}.static"
                            item = name
                        except TypeError as e:
                            logging.getLogger(__name__).error(
                                f"Blueprint '{blueprint_name}' has no static folder "
                                f"for asset '{original_item}': {e}"
                            )
                            raise TypeError(
                                f"Blueprint '{blueprint_name}' has no static folder"
                            ) from e
                    else:
                        logging.getLogger(__name__).debug(
                            f"Blueprint '{blueprint_name}' not found, "
                            f"treating '{original_item}' as app-level path"
                        )
                        directory = get_static_folder(app)
                        endpoint = "static"
                        item = original_item

                except ValueError as e:
                    logging.getLogger(__name__).debug(
                        f"Invalid blueprint prefix format in '{original_item}': {e}, "
                        "falling back to app static"
                    )
                    directory = get_static_folder(app)
                    endpoint = "static"
                    item = original_item
            else:
                # No blueprints support or no prefix, use app static
                directory = get_static_folder(app)
                endpoint = "static"

        except TypeError as e:
            logging.getLogger(__name__).error(
                f"Failed to get static folder for app when processing '{original_item}': {e}"
            )
            raise TypeError("App has no static folder configured") from e
        except Exception as e:
            logging.getLogger(__name__).error(
                f"Unexpected error processing '{original_item}': {e}, falling back to app static"
            )
            try:
                directory = get_static_folder(app)
                endpoint = "static"
                item = original_item
            except TypeError as te:
                raise TypeError("App has no static folder configured") from te

        return directory, item, endpoint

    def use_webassets_system_for_output(self, ctx: Any) -> bool:
        return ctx.config.get("directory") is not None or ctx.config.get("url") is not None

    def use_webassets_system_for_sources(self, ctx: Any) -> bool:
        return bool(ctx.load_path)

    def search_for_source(self, ctx: Any, item: str) -> Any:
        # If a load_path is set, use it instead of the Quart static system.
        #
        # Note: With only env.directory set, we don't go to default;
        # Setting env.directory only makes the output directory fixed.
        if self.use_webassets_system_for_sources(ctx):
            return Resolver.search_for_source(self, ctx, item)

        # Look in correct blueprint's directory
        directory, item, endpoint = self.split_prefix(ctx, item)
        try:
            return self.consider_single_directory(directory, item)
        except IOError:
            # XXX: Hack to make the tests pass, which are written to not
            # expect an IOError upon missing files. They need to be rewritten.
            return path.normpath(path.join(directory, item))

    def resolve_output_to_path(self, ctx: Any, target: str, bundle: Any) -> Any:
        # If a directory/url pair is set, always use it for output files
        if self.use_webassets_system_for_output(ctx):
            return Resolver.resolve_output_to_path(self, ctx, target, bundle)

        # Allow targeting blueprint static folders
        directory, rel_path, endpoint = self.split_prefix(ctx, target)
        return path.normpath(path.join(directory, rel_path))

    def resolve_source_to_url(self, ctx: Any, filepath: str, item: str) -> str:
        # If a load path is set, use it instead of the Quart static system.
        if self.use_webassets_system_for_sources(ctx):
            return super().resolve_source_to_url(ctx, filepath, item)

        return self.convert_item_to_quart_url(ctx, item, filepath)

    def resolve_output_to_url(self, ctx: Any, target: str) -> str:
        # With a directory/url pair set, use it for output files.
        if self.use_webassets_system_for_output(ctx):
            return Resolver.resolve_output_to_url(self, ctx, target)

        # Otherwise, behaves like all other Quart URLs.
        return self.convert_item_to_quart_url(ctx, target)

    def convert_item_to_quart_url(self, ctx: Any, item: str, filepath: Optional[str] = None) -> str:
        """Given a relative reference like `foo/bar.css`, returns
        the Quart static url. By doing so it takes into account
        blueprints, i.e. in the aformentioned example,
        ``foo`` may reference a blueprint.

        If an absolute path is given via ``filepath``, it will be
        used instead. This is needed because ``item`` may be a
        glob instruction that was resolved to multiple files.
        """
        from quart import has_request_context, url_for

        directory, rel_path, endpoint = self.split_prefix(ctx, item)

        if filepath is not None:
            filename = filepath[len(directory) + 1 :]
        else:
            filename = rel_path

        # Windows compatibility
        filename = filename.replace("\\", "/")

        if has_request_context():
            # We're already in a request context, use it directly
            url = url_for(endpoint, filename=filename)
        else:
            # Fallback to manual URL construction when no request context
            # This handles both sync and async contexts
            app = ctx.environment._app

            # Handle blueprint URLs
            if endpoint.endswith(".static"):
                # This is a blueprint static endpoint
                bp_name = endpoint[:-7]  # Remove '.static' suffix
                if hasattr(app, "blueprints") and bp_name in app.blueprints:
                    bp = app.blueprints[bp_name]
                    static_url_path = getattr(bp, "static_url_path", None)
                    if static_url_path:
                        url = f"{static_url_path}/{filename}"
                    else:
                        # Use blueprint name as prefix
                        url = f"/{bp_name}/{filename}"
                else:
                    # Fallback to app static path
                    url = f"{app.static_url_path}/{filename}"
            else:
                # Regular app static endpoint
                url = f"{app.static_url_path}/{filename}"

        # In some cases, url will be an absolute url with a scheme and
        # hostname. (for example, when using werkzeug's host matching).
        # In general, url_for() will return a http url. During assets build,
        # we don't know yet if the assets will be served over http, https
        # or both. Let's use // instead. url_for takes a _scheme argument,
        # but only together with external=True, which we do not want to
        # force every time. Further, # this _scheme argument is not able to
        # render // - it always forces a colon.
        if url and url.startswith("http:"):
            url = url[5:]
        return url


class QuartAssets(BaseEnvironment):  # type: ignore[misc]
    """This object is used to hold a collection of bundles and configuration.

    If initialized with a Quart app instance then a webassets Jinja2 extension
    is automatically registered.
    """

    config_storage_class = QuartConfigStorage
    resolver_class = QuartResolver

    def __init__(self, app: Optional[Quart] = None) -> None:
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

    def get_url(self) -> Optional[str]:
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
        app.jinja_env.assets_environment = self  # type: ignore[attr-defined]

    def from_yaml(self, path: str) -> None:
        """Register bundles from a YAML configuration file"""
        bundles = YAMLLoader(path).load_bundles()
        for name, bundle in bundles.items():
            self.register(name, bundle)

    def from_module(self, path: Union[str, Any]) -> None:
        """Register bundles from a Python module"""
        bundles = PythonLoader(path).load_bundles()
        for name, bundle in bundles.items():
            self.register(name, bundle)


# Override the built-in ``jinja2`` filter that ships with ``webassets``. This
# custom filter uses Quart's ``render_template_string`` function to provide all
# the standard Quart template context variables.
register_filter(Jinja2Filter)


try:
    import click
except ImportError:
    pass
else:

    def _webassets_cmd(cmd: str, info: ScriptInfo) -> None:
        """Helper to run a webassets command."""
        app = info.load_app()

        if not hasattr(app.jinja_env, "assets_environment"):
            raise RuntimeError(
                "No assets environment found. Make sure you've "
                + "initialized QuartAssets with your app."
            )

        logger = logging.getLogger("webassets")
        logger.addHandler(logging.StreamHandler())
        logger.setLevel(logging.DEBUG)

        async def _run_with_app_context() -> None:
            async with app.app_context():
                cmdenv = CommandLineEnvironment(
                    app.jinja_env.assets_environment, logger  # type: ignore[attr-defined]
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

    __all__.extend(["assets", "build", "clean", "watch"])
