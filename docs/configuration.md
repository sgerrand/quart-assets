# Configuration

Quart-Assets can be configured through Quart's configuration system. All
configuration keys are prefixed with `ASSETS_`.

## Basic Configuration

### Debug Mode

Control whether assets are served individually or as bundles:

```python
app.config['ASSETS_DEBUG'] = False  # Default: serve bundles
app.config['ASSETS_DEBUG'] = True   # Development: serve individual files
```

### Auto Build

Control when assets are automatically rebuilt:

```python
app.config['ASSETS_AUTO_BUILD'] = True   # Default: auto-rebuild when needed
app.config['ASSETS_AUTO_BUILD'] = False  # Manual building only
```

### Cache Directory

Set where compiled assets are stored:

```python
app.config['ASSETS_CACHE'] = '/tmp/assets-cache'  # Custom cache directory
```

### URL Generation

Configure how asset URLs are generated:

```python
app.config['ASSETS_URL'] = '/static'      # Base URL for assets
app.config['ASSETS_URL_EXPIRE'] = True    # Add timestamps to URLs
```

## Directory Configuration

### Custom Directories

Override the default static directory:

```python
from quart_assets import QuartAssets

app = Quart(__name__)
assets = QuartAssets(app)

# Set custom directories
assets.directory = '/path/to/assets'
assets.url = '/assets'
```

### Load Path

Add additional directories to search for source files:

```python
assets.append_path('/path/to/vendor/assets')
assets.append_path('/path/to/shared/assets', '/shared-assets')
```

## Environment-Based Configuration

### Development Settings

```python
class DevelopmentConfig:
    ASSETS_DEBUG = True
    ASSETS_AUTO_BUILD = True
    ASSETS_CACHE = False  # Disable caching for development
```

### Production Settings

```python
class ProductionConfig:
    ASSETS_DEBUG = False
    ASSETS_AUTO_BUILD = True
    ASSETS_CACHE = True
    ASSETS_URL_EXPIRE = True  # Cache busting
```

### Testing Settings

```python
class TestingConfig:
    ASSETS_DEBUG = True
    ASSETS_AUTO_BUILD = False  # Manual control in tests
    ASSETS_CACHE = False
```

## Blueprint Configuration

When using blueprints, assets can reference blueprint-specific directories:

```python
from quart import Blueprint

# Create blueprint with static folder
admin_bp = Blueprint('admin', __name__, 
                    static_folder='static',
                    static_url_path='/admin/static')

# Register blueprint-specific assets
admin_css = Bundle('admin/styles.css', output='admin/admin.min.css')
assets.register('admin_css', admin_css)
```

## Advanced Configuration

### Custom Resolvers

For complex directory structures, you can customize how files are resolved:

```python
from quart_assets import QuartAssets

class CustomResolver(QuartResolver):
    def resolve_source_to_url(self, ctx, filepath, item):
        # Custom URL resolution logic
        return super().resolve_source_to_url(ctx, filepath, item)

assets = QuartAssets()
assets.resolver_class = CustomResolver
```

### Configuration Storage

Customize how configuration is stored and accessed:

```python
from quart_assets.extension import QuartConfigStorage

class CustomConfigStorage(QuartConfigStorage):
    def __getitem__(self, key):
        # Custom configuration logic
        return super().__getitem__(key)

assets.config_storage_class = CustomConfigStorage
```

## YAML Configuration

You can also define bundles in YAML files:

```yaml
# assets.yml
css_bundle:
  filters: cssmin
  output: dist/all.min.css
  contents:
    - css/main.css
    - css/utils.css

js_bundle:
  filters: jsmin
  output: dist/all.min.js
  contents:
    - js/main.js
    - js/utils.js
```

Load the YAML configuration:

```python
assets.from_yaml('assets.yml')
```

## Python Module Configuration

Define bundles in a Python module:

```python
# assets_config.py
from quart_assets import Bundle

bundles = {
    'css_all': Bundle(
        'css/main.css',
        'css/utils.css',
        filters='cssmin',
        output='dist/all.min.css'
    ),
    'js_all': Bundle(
        'js/main.js',
        filters='jsmin',
        output='dist/all.min.js'
    )
}
```

Load the module configuration:

```python
assets.from_module('assets_config')
```

## Configuration Reference

| Setting | Default | Description |
|---------|---------|-------------|
| `ASSETS_DEBUG` | `False` | Serve individual files instead of bundles |
| `ASSETS_AUTO_BUILD` | `True` | Automatically rebuild assets when needed |
| `ASSETS_CACHE` | `True` | Enable asset caching |
| `ASSETS_URL_EXPIRE` | `True` | Add timestamps to URLs for cache busting |
| `ASSETS_DIRECTORY` | `app.static_folder` | Directory where assets are stored |
| `ASSETS_URL` | `app.static_url_path` | Base URL for serving assets |
| `ASSETS_LOAD_PATH` | `[]` | Additional directories to search for source files |

## Next Steps

- [CLI Commands](cli.md) - Learn about command-line tools
- [API Reference](api/environment.md) - Detailed API documentation
- [Examples](examples.md) - See configuration in action
