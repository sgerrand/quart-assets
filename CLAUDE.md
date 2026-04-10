# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Quart-Assets is a Python library that integrates the `webassets` library with
the Quart web framework, providing support for merging, minifying and compiling
CSS and Javascript files. This is a port of Flask-Assets for the Quart async web
framework.

## Architecture

- **Core module**: `src/quart_assets/extension.py` - Single module containing all functionality
- **Main classes**:
  - `Environment`: Central class that manages bundles and configuration, integrates with Quart app
  - `QuartResolver`: Handles Quart blueprint-aware file resolution and URL generation  
  - `QuartConfigStorage`: Uses Quart app config as backend for webassets configuration
  - `Jinja2Filter`: Custom filter that uses Quart's template context for Jinja2 processing
- **CLI commands**: Provides `quart assets build/clean/watch` commands via Quart's CLI system
- **Blueprint support**: Full integration with Quart blueprints for static file management

## Development Commands

### Testing
```bash
# Run all tests
tox -e py

# Run tests with tox (multiple Python versions)
tox

# Run specific test file
tox -e py -- tests/test_integration.py
```

### Dependencies
```bash
# Install development dependencies
uv sync

# Update dependencies
uv sync --upgrade
```

### Asset Management Commands
When working with a Quart app that uses this extension:
```bash
# Build all asset bundles
quart assets build

# Clean generated bundles
quart assets clean

# Watch for changes and rebuild automatically
quart assets watch
```

## Testing Structure

- Tests use pytest with fixtures defined in `tests/conftest.py`
- Key fixtures: `app` (Quart app with blueprint), `env` (Environment instance), `temp_dir`
- Test blueprint in `tests/bp_for_test/` for blueprint-related functionality
- Integration tests in `test_integration.py` test full asset pipeline

## Key Configuration

- **Entry point**: `pyproject.toml` defines `quart.commands` entry point for CLI integration
- **Version**: Managed via `__version__` tuple in `src/quart_assets/__init__.py` 
- **Dependencies**: Core deps are Quart>=0.8 and webassets>=2.0
- **Python support**: 3.10, 3.11, 3.12, 3.13 (defined in tox.ini)

## Notable Implementation Details

- Automatically registers Jinja2 extension when Environment is initialized with app
- Custom resolver supports blueprint prefixes (e.g., "blueprint_name/file.css")
- Handles both app-bound and current-app-context usage patterns
- Windows path compatibility built into URL generation
- Custom Jinja2 filter provides full Quart template context during asset processing
