# Quart-Assets

Quart-Assets is an extension for [Quart][quart] that supports merging,
minifying and compiling CSS and Javascript files via the
[`webassets`][webassets] library.

## Usage

To use Quart-Assets with a Quart app, you have to create a QuartAssets
instance and initialise it with the application:

```python
from quart import Quart
from quart_assets import Bundle, QuartAssets

app = Quart(__name__)
assets = QuartAssets(app)

js_bundle = Bundle('alpine.js', 'main.js', 'utils.js',
                   filters='jsmin', output='dist/all.min.js')
assets.register('js_all', js_bundle)
```

A bundle consists of any number of source files (it may also contain other
nested bundles), an output target, and a list of filters to apply.

All paths are relative to your app’s static directory, or the static directory of a Quart blueprint.


[quart]: https://quart.palletprojects.com
[webassets]: https://webassets.readthedocs.io
