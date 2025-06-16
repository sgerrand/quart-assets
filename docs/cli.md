# CLI Commands

Quart-Assets provides several command-line tools to help you manage your assets.
These commands integrate with Quart's CLI system.

## Basic Usage

All Quart-Assets CLI commands are accessed through the `quart assets` command:

```bash
python -m quart assets --help
```

## Available Commands

### build

Build all registered asset bundles:

```bash
python -m quart assets build
```

This command:
- Processes all registered bundles
- Applies configured filters (minification, compilation, etc.)
- Outputs the final bundled files
- Reports any errors or warnings

Example output:
```
Building bundle: css_all
Building bundle: js_all
Built 2 bundles successfully
```

### clean

Remove all generated asset files:

```bash
python -m quart assets clean
```

This command:
- Removes all output files created by bundles
- Cleans the cache directory
- Reports which files were deleted

Example output:
```
Cleaning generated assets...
Deleted asset: dist/all.min.css
Deleted asset: dist/all.min.js
Cleaned 2 assets
```

### watch

Watch source files for changes and automatically rebuild:

```bash
python -m quart assets watch
```

This command:
- Monitors all source files for changes
- Automatically rebuilds affected bundles when files change
- Runs continuously until stopped (Ctrl+C)
- Useful during development

Example output:
```
Watching assets for changes...
Change detected in css/main.css, rebuilding css_all...
Built css_all successfully
```

## Environment Setup

The CLI commands need access to your Quart application. Set the `QUART_APP` environment variable:

```bash
export QUART_APP=myapp.py
python -m quart assets build
```

Or use it inline:

```bash
QUART_APP=myapp.py python -m quart assets build
```

## Application Factory Pattern

If you're using an application factory, you can specify the factory function:

```bash
export QUART_APP="myapp:create_app"
python -m quart assets build
```

## Configuration

The CLI commands respect your application's configuration. You can set different
configurations for different environments:

```python
# config.py
class DevelopmentConfig:
    ASSETS_DEBUG = True
    ASSETS_AUTO_BUILD = True

class ProductionConfig:
    ASSETS_DEBUG = False
    ASSETS_AUTO_BUILD = True
```

```bash
export QUART_ENV=development
export QUART_APP=myapp.py
python -m quart assets build
```

## Integration with Development Workflow

### Development Workflow

During development, use the watch command to automatically rebuild assets:

```bash
# Terminal 1: Run your Quart app
python -m quart run --debug

# Terminal 2: Watch for asset changes
python -m quart assets watch
```

### Production Deployment

For production deployments, build assets as part of your deployment process:

```bash
# Build assets for production
QUART_ENV=production python -m quart assets build

# Then start your production server
gunicorn -k quart.worker.QuartWorker myapp:app
```

### CI/CD Pipeline

Example GitHub Actions workflow:

```yaml
name: Build and Test
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        pip install -e .
        pip install pytest
    
    - name: Build assets
      run: python -m quart assets build
      env:
        QUART_APP: myapp.py
    
    - name: Run tests
      run: pytest
```

## Troubleshooting

### Command Not Found

If you get "No such command 'assets'", ensure:
- Quart-Assets is installed: `pip install quart-assets`
- Your app imports and initializes QuartAssets
- The `QUART_APP` environment variable is set correctly

### Assets Not Building

If assets aren't building:
- Check that source files exist in the correct paths
- Verify bundle registration in your app
- Look for error messages in the command output
- Ensure required filters are installed (e.g., `jsmin`, `cssmin`)

### Permission Errors

If you get permission errors:
- Check write permissions on the output directory
- Ensure the static folder is writable
- Consider using a different output directory

### Import Errors

If you get import errors:
- Ensure all dependencies are installed
- Check that your app can be imported normally
- Verify the Python path includes your project directory

## Examples

### Basic Project

```bash
# Project structure
myproject/
├── app.py
├── static/
│   ├── css/
│   └── js/
└── templates/

# Build assets
QUART_APP=app.py python -m quart assets build
```

### Blueprint Project

```bash
# Project with blueprints
myproject/
├── app.py
├── main/
│   ├── __init__.py
│   └── static/
├── admin/
│   ├── __init__.py
│   └── static/
└── templates/

# Build all assets (including blueprint assets)
QUART_APP=app.py python -m quart assets build
```

### Using Make

Create a Makefile for common tasks:

```makefile
# Makefile
.PHONY: assets clean watch

assets:
	python -m quart assets build

clean:
	python -m quart assets clean

watch:
	python -m quart assets watch

dev: assets
	python -m quart run --debug
```

Then use:
```bash
make assets  # Build assets
make clean   # Clean assets
make watch   # Watch for changes
make dev     # Build and run development server
```

## Next Steps

- [Examples](examples.md) - See CLI commands in real projects
- [API Reference](api/cli.md) - Detailed CLI API documentation
- [Configuration](configuration.md) - Configure asset building behavior
