# Quick Start

This guide will get you up and running with Quart-Assets in just a few minutes.

## Basic Setup

### 1. Create a Quart App

First, create a basic Quart application:

```python
from quart import Quart, render_template

app = Quart(__name__)

@app.route('/')
async def index():
    return await render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
```

### 2. Initialize Quart-Assets

Add Quart-Assets to your application:

```python
from quart import Quart, render_template
from quart_assets import QuartAssets, Bundle

app = Quart(__name__)
assets = QuartAssets(app)

@app.route('/')
async def index():
    return await render_template('index.html')
```

### 3. Create Asset Files

Create some CSS and JavaScript files in your `static` directory:

```css
/* static/css/main.css */
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
}

.header {
    background-color: #333;
    color: white;
    padding: 1rem;
}
```

```css
/* static/css/utils.css */
.btn {
    background-color: #007bff;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.btn:hover {
    background-color: #0056b3;
}
```

```javascript
/* static/js/main.js */
document.addEventListener('DOMContentLoaded', function() {
    console.log('App initialized');
});

function showMessage(message) {
    alert(message);
}
```

### 4. Create Bundles

Define your asset bundles:

```python
from quart import Quart, render_template
from quart_assets import QuartAssets, Bundle

app = Quart(__name__)
assets = QuartAssets(app)

# CSS Bundle
css_bundle = Bundle(
    'css/main.css',
    'css/utils.css',
    filters='cssmin',
    output='dist/all.min.css'
)

# JavaScript Bundle
js_bundle = Bundle(
    'js/main.js',
    filters='jsmin', 
    output='dist/all.min.js'
)

# Register bundles
assets.register('css_all', css_bundle)
assets.register('js_all', js_bundle)

@app.route('/')
async def index():
    return await render_template('index.html')
```

### 5. Use in Templates

Create a template that uses your bundles:

```html
<!-- templates/index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Quart-Assets Demo</title>
    {% assets "css_all" %}
        <link rel="stylesheet" href="{{ ASSET_URL }}">
    {% endassets %}
</head>
<body>
    <div class="header">
        <h1>Welcome to Quart-Assets!</h1>
    </div>
    
    <div class="content">
        <p>Your assets are bundled and minified automatically.</p>
        <button class="btn" onclick="showMessage('Hello from bundled JS!')">
            Click me!
        </button>
    </div>

    {% assets "js_all" %}
        <script src="{{ ASSET_URL }}"></script>
    {% endassets %}
</body>
</html>
```

## Development vs Production

### Development Mode

In development, you typically want to see individual files for debugging:

```python
app.config['ASSETS_DEBUG'] = True  # Serve individual files
```

### Production Mode

In production, you want optimized bundles:

```python
app.config['ASSETS_DEBUG'] = False  # Serve bundled files
app.config['ASSETS_AUTO_BUILD'] = True  # Auto-build when needed
```

## Using the CLI

Quart-Assets provides CLI commands for managing your assets:

```bash
# Build all bundles
python -m quart assets build

# Clean generated files
python -m quart assets clean

# Watch for changes (useful in development)
python -m quart assets watch
```

## Directory Structure

After following this guide, your project should look like this:

```
your-app/
├── app.py
├── static/
│   ├── css/
│   │   ├── main.css
│   │   └── utils.css
│   ├── js/
│   │   └── main.js
│   └── dist/           # Generated bundles
│       ├── all.min.css
│       └── all.min.js
└── templates/
    └── index.html
```

## Next Steps

- [Configuration](configuration.md) - Learn about advanced configuration options
- [CLI Commands](cli.md) - Explore all available CLI commands
- [API Reference](api/environment.md) - Dive deeper into the API
- [Examples](examples.md) - See more complex examples