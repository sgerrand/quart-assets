# CLI API

This page documents the command-line interface functions and classes.

## CLI Commands

The CLI commands are implemented as Click commands that integrate with Quart's CLI system.

### assets

::: quart_assets.extension.assets
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

### build

::: quart_assets.extension.build
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

### clean

::: quart_assets.extension.clean
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

### watch

::: quart_assets.extension.watch
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

## Helper Functions

### _webassets_cmd

::: quart_assets.extension._webassets_cmd
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

## Usage Examples

### Basic Command Usage

```bash
# Show help for all asset commands
python -m quart assets --help

# Build all asset bundles
python -m quart assets build

# Clean generated assets
python -m quart assets clean

# Watch for changes and rebuild automatically
python -m quart assets watch
```

### Environment Configuration

```bash
# Set the Quart application
export QUART_APP=myapp.py

# Set environment
export QUART_ENV=production

# Run commands
python -m quart assets build
```

### Application Factory

```bash
# For application factory pattern
export QUART_APP="myapp:create_app"
python -m quart assets build
```

### Programmatic Usage

While the CLI commands are typically used from the command line, you can also
access the underlying functionality programmatically:

```python
from quart_assets.extension import _webassets_cmd
from quart.cli import ScriptInfo

# Create script info (normally done by Quart CLI)
info = ScriptInfo(name='myapp')

# Run commands programmatically
_webassets_cmd('build', info)
_webassets_cmd('clean', info)
```

## Error Handling

The CLI commands include error handling for common issues:

- **Application not found**: Ensures `QUART_APP` is set correctly
- **Assets environment missing**: Verifies `QuartAssets` is initialized
- **File permission errors**: Provides clear error messages
- **Import errors**: Handles missing dependencies gracefully

## Integration

### CI/CD Pipelines

Example usage in continuous integration:

```yaml
# .github/workflows/build.yml
- name: Build assets
  run: python -m quart assets build
  env:
    QUART_APP: myapp.py
    QUART_ENV: production
```

### Docker

Example Dockerfile integration:

```dockerfile
# Build assets during image build
RUN QUART_APP=myapp.py python -m quart assets build

# Or build at runtime
CMD ["sh", "-c", "python -m quart assets build && python -m quart run"]
```

### Development Scripts

Example development script:

```bash
#!/bin/bash
# dev.sh

export QUART_APP=myapp.py
export QUART_ENV=development

# Build assets
python -m quart assets build

# Start development server
python -m quart run --debug
```

## Next Steps

- [CLI Commands Guide](../cli.md) - Detailed CLI usage guide
- [Configuration](../configuration.md) - Configure CLI behavior
- [Examples](../examples.md) - See CLI in action
