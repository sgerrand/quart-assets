# Quart-Assets

[![Build Status](https://github.com/sgerrand/quart-assets/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/sgerrand/quart-assets/actions/workflows/tests.yml)
[![License](https://img.shields.io/badge/License-BSD%202--Clause-blue.svg)](https://opensource.org/licenses/BSD-2-Clause)
[![PyPI version](https://badge.fury.io/py/quart-assets.svg)](https://badge.fury.io/py/quart-assets)

Quart-Assets is an extension for [Quart][quart] that supports merging,
minifying and compiling CSS and Javascript files via the
[`webassets`][webassets] library.

## Features

- **Asset bundling**: Combine multiple CSS and JavaScript files into single bundles
- **Minification**: Reduce file sizes with built-in minification filters
- **Compilation**: Support for SCSS, Less, CoffeeScript, and other preprocessors
- **Blueprint support**: Full integration with Quart blueprints
- **CLI commands**: Build, clean, and watch assets from the command line
- **Development mode**: Automatic rebuilding during development
- **Async support**: Built for Quart's async architecture

## Quick Example

```python
from quart import Quart
from quart_assets import Bundle, QuartAssets

app = Quart(__name__)
assets = QuartAssets(app)

# Create CSS bundle
css_bundle = Bundle('src/main.css', 'src/utils.css',
                   filters='cssmin', output='dist/all.min.css')

# Create JavaScript bundle
js_bundle = Bundle('src/alpine.js', 'src/main.js', 'src/utils.js',
                   filters='jsmin', output='dist/all.min.js')

# Register bundles
assets.register('css_all', css_bundle)
assets.register('js_all', js_bundle)
```

## Why Quart-Assets?

Quart-Assets is a port of the popular Flask-Assets extension, specifically
designed for Quart's async architecture. It provides:

- **Seamless integration** with Quart applications and blueprints
- **Async-aware** template processing and CLI commands
- **Production-ready** asset optimization and caching
- **Developer-friendly** tools for asset management

[quart]: https://quart.palletprojects.com
[webassets]: https://webassets.readthedocs.io
