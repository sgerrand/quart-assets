# Installation

## Requirements

- Python 3.10+
- Quart 0.20.0+
- webassets 2.0+

## Install from PyPI

The recommended way to install Quart-Assets is from PyPI using pip:

```bash
pip install quart-assets
```

## Install from Source

You can also install directly from the GitHub repository:

```bash
pip install git+https://github.com/sgerrand/quart-assets.git
```

For development, clone the repository and install in editable mode:

```bash
git clone https://github.com/sgerrand/quart-assets.git
cd quart-assets
pip install -e .
```

## Dependencies

Quart-Assets automatically installs these core dependencies:

- **Quart**: The async web framework
- **webassets**: The underlying asset management library
- **PyYAML**: For YAML configuration files
- **pyscss**: For SCSS compilation support

## Optional Dependencies

Depending on your needs, you may want to install additional filters:

### JavaScript Minification
```bash
pip install jsmin          # Basic JS minification
pip install rjsmin         # Faster JS minification
```

### CSS Processing
```bash
pip install cssmin         # CSS minification
pip install libsass        # Sass/SCSS compilation
```

### Development Tools
```bash
pip install watchdog       # File watching for auto-rebuild
```

## Verification

To verify your installation, you can import Quart-Assets in Python:

```python
from quart_assets import QuartAssets, Bundle
print("Quart-Assets installed successfully!")
```

Or check the CLI commands are available:

```bash
python -c "from quart_assets.extension import assets; print('CLI available')"
```

## Next Steps

Once installed, head to the [Quick Start Guide](quickstart.md) to create your first asset bundles.
