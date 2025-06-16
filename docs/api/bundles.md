# Bundle Management

This page documents the Bundle class and related functionality for managing asset bundles.

## Bundle Class

The `Bundle` class is imported from the webassets library and represents a
collection of asset files that should be processed together.

```python
from quart_assets import Bundle

# Basic bundle
css_bundle = Bundle('css/main.css', 'css/utils.css', 
                   output='dist/all.css')

# Bundle with filters
js_bundle = Bundle('js/main.js', 'js/utils.js',
                  filters='jsmin', output='dist/all.min.js')
```

For detailed documentation of the Bundle class, see the [webassets
documentation](https://webassets.readthedocs.io/en/latest/bundles.html).

## Bundle Registration

Bundles are registered with the QuartAssets environment using the `register` method:

```python
from quart_assets import QuartAssets, Bundle

assets = QuartAssets(app)

# Register a bundle
bundle = Bundle('css/main.css', output='dist/main.css')
assets.register('main_css', bundle)

# Access registered bundles
main_css_bundle = assets['main_css']
```

## Bundle Configuration

### Basic Configuration

```python
Bundle(
    'source1.css',           # Source files
    'source2.css',
    output='output.css',     # Output file
    filters='cssmin',        # Filters to apply
    debug=False,            # Debug mode override
    depends='config.yml'     # Dependencies
)
```

### Advanced Configuration

```python
Bundle(
    'js/vendor/jquery.js',
    'js/vendor/bootstrap.js',
    Bundle(                  # Nested bundles
        'js/app/main.js',
        'js/app/utils.js',
        filters='jsmin'
    ),
    filters=['babel', 'jsmin'],  # Multiple filters
    output='dist/app.min.js',
    extra={                      # Extra metadata
        'async': True,
        'defer': True
    }
)
```

## Common Bundle Patterns

### CSS Bundles

```python
# Basic CSS bundle
css_main = Bundle('css/main.css', 'css/layout.css',
                 filters='cssmin', output='dist/main.min.css')

# SCSS compilation
scss_bundle = Bundle('scss/main.scss',
                    filters='pyscss,cssmin', 
                    output='dist/compiled.min.css')

# Vendor CSS
vendor_css = Bundle('vendor/bootstrap.css', 'vendor/fontawesome.css',
                   filters='cssmin', output='dist/vendor.min.css')
```

### JavaScript Bundles

```python
# Application JS
app_js = Bundle('js/app.js', 'js/components/*.js',
               filters='jsmin', output='dist/app.min.js')

# Vendor libraries
vendor_js = Bundle('vendor/jquery.js', 'vendor/bootstrap.js',
                  filters='jsmin', output='dist/vendor.min.js')

# Modern JS with Babel
modern_js = Bundle('js/es6/*.js',
                  filters='babel,jsmin', output='dist/modern.min.js')
```

### Blueprint-Specific Bundles

```python
# Reference blueprint assets using blueprint prefix
admin_css = Bundle('admin/styles.css', 'admin/layout.css',
                  filters='cssmin', output='admin/admin.min.css')

admin_js = Bundle('admin/main.js', 'admin/dashboard.js',
                 filters='jsmin', output='admin/admin.min.js')
```

## Bundle Loading

### From Python

```python
# Direct bundle creation
bundles = {
    'css_main': Bundle('css/main.css', output='dist/main.css'),
    'js_main': Bundle('js/main.js', output='dist/main.js')
}

for name, bundle in bundles.items():
    assets.register(name, bundle)
```

### From YAML

```yaml
# bundles.yml
css_main:
  contents:
    - css/main.css
    - css/layout.css
  output: dist/main.min.css
  filters: cssmin

js_main:
  contents:
    - js/main.js
    - js/utils.js
  output: dist/main.min.js
  filters: jsmin
```

```python
assets.from_yaml('bundles.yml')
```

### From Module

```python
# bundles_config.py
from quart_assets import Bundle

bundles = {
    'css_main': Bundle('css/main.css', filters='cssmin', 
                      output='dist/main.min.css'),
    'js_main': Bundle('js/main.js', filters='jsmin',
                     output='dist/main.min.js')
}
```

```python
assets.from_module('bundles_config')
```

## Bundle Operations

### Building Bundles

```python
# Build a specific bundle
bundle = assets['css_main']
bundle.build()

# Build all bundles
for bundle in assets:
    bundle.build()
```

### Bundle URLs

```python
# Get URLs for a bundle
bundle = assets['css_main']
urls = bundle.urls()  # Returns list of URLs

# In templates, this is handled automatically
# {% assets "css_main" %}
#   <link rel="stylesheet" href="{{ ASSET_URL }}">
# {% endassets %}
```

### Bundle Contents

```python
# Get source files for a bundle
bundle = assets['css_main']
contents = bundle.contents  # List of source files

# Resolve globbed files
from webassets.bundle import get_all_bundle_files
all_files = get_all_bundle_files(bundle, assets)
```

## Next Steps

- [CLI API](cli.md) - Command-line interface documentation
- [Configuration](../configuration.md) - Bundle configuration options
- [Examples](../examples.md) - Real-world bundle examples
