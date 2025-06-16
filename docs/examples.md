# Examples

This page provides real-world examples of using Quart-Assets in different scenarios.

## Basic Web Application

### Simple Blog

A basic blog application with CSS and JavaScript bundling:

```python
# app.py
from quart import Quart, render_template
from quart_assets import QuartAssets, Bundle

app = Quart(__name__)
assets = QuartAssets(app)

# CSS Bundle
css_bundle = Bundle(
    'css/reset.css',
    'css/base.css', 
    'css/blog.css',
    filters='cssmin',
    output='dist/blog.min.css'
)

# JavaScript Bundle
js_bundle = Bundle(
    'js/jquery.min.js',
    'js/blog.js',
    filters='jsmin',
    output='dist/blog.min.js'
)

assets.register('css_all', css_bundle)
assets.register('js_all', js_bundle)

@app.route('/')
async def index():
    return await render_template('index.html')

@app.route('/post/<int:post_id>')
async def post(post_id):
    return await render_template('post.html', post_id=post_id)

if __name__ == '__main__':
    app.run(debug=True)
```

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html>
<head>
    <title>My Blog</title>
    {% assets "css_all" %}
        <link rel="stylesheet" href="{{ ASSET_URL }}">
    {% endassets %}
</head>
<body>
    <header>
        <h1>My Blog</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/about">About</a>
        </nav>
    </header>
    
    <main>
        {% block content %}{% endblock %}
    </main>
    
    <footer>
        <p>&copy; 2024 My Blog</p>
    </footer>

    {% assets "js_all" %}
        <script src="{{ ASSET_URL }}"></script>
    {% endassets %}
</body>
</html>
```

## Multi-Blueprint Application

### E-commerce Site

An e-commerce application with separate admin and frontend assets:

```python
# app.py
from quart import Quart
from quart_assets import QuartAssets, Bundle

def create_app():
    app = Quart(__name__)
    assets = QuartAssets(app)
    
    # Register blueprints
    from .frontend import frontend_bp
    from .admin import admin_bp
    
    app.register_blueprint(frontend_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Frontend assets
    frontend_css = Bundle(
        'frontend/css/bootstrap.css',
        'frontend/css/shop.css',
        'frontend/css/product.css',
        filters='cssmin',
        output='dist/frontend.min.css'
    )
    
    frontend_js = Bundle(
        'frontend/js/vendor/jquery.js',
        'frontend/js/vendor/bootstrap.js',
        'frontend/js/shop.js',
        'frontend/js/cart.js',
        filters='jsmin',
        output='dist/frontend.min.js'
    )
    
    # Admin assets (blueprint-specific)
    admin_css = Bundle(
        'admin/css/admin.css',
        'admin/css/dashboard.css',
        filters='cssmin',
        output='admin/admin.min.css'
    )
    
    admin_js = Bundle(
        'admin/js/admin.js',
        'admin/js/charts.js',
        filters='jsmin',
        output='admin/admin.min.js'
    )
    
    # Register bundles
    assets.register('frontend_css', frontend_css)
    assets.register('frontend_js', frontend_js)
    assets.register('admin_css', admin_css)
    assets.register('admin_js', admin_js)
    
    return app
```

```python
# frontend/__init__.py
from quart import Blueprint

frontend_bp = Blueprint(
    'frontend', 
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/frontend'
)

from . import routes
```

```python
# admin/__init__.py
from quart import Blueprint

admin_bp = Blueprint(
    'admin',
    __name__,
    template_folder='templates', 
    static_folder='static',
    static_url_path='/admin/static'
)

from . import routes
```

## Advanced SCSS/JavaScript Compilation

### Modern Frontend

A modern web application using SCSS and ES6+ JavaScript:

```python
# app.py
from quart import Quart
from quart_assets import QuartAssets, Bundle

app = Quart(__name__)
assets = QuartAssets(app)

# Configure for development vs production
if app.debug:
    app.config['ASSETS_DEBUG'] = True
else:
    app.config['ASSETS_DEBUG'] = False
    app.config['ASSETS_AUTO_BUILD'] = True

# SCSS compilation bundle
scss_bundle = Bundle(
    'scss/main.scss',
    filters='pyscss,cssmin',
    output='dist/app.min.css'
)

# Modern JavaScript with Babel
js_modern = Bundle(
    'js/src/app.js',
    'js/src/components/*.js',
    'js/src/utils/*.js',
    filters='babel,jsmin',
    output='dist/app.modern.min.js'
)

# Vendor libraries (no compilation needed)
vendor_css = Bundle(
    'vendor/normalize.css',
    'vendor/fontawesome.css',
    filters='cssmin',
    output='dist/vendor.min.css'
)

vendor_js = Bundle(
    'vendor/vue.js',
    'vendor/axios.js',
    filters='jsmin',
    output='dist/vendor.min.js'
)

assets.register('app_css', scss_bundle)
assets.register('app_js', js_modern)
assets.register('vendor_css', vendor_css)
assets.register('vendor_js', vendor_js)
```

```scss
/* static/scss/main.scss */
@import 'variables';
@import 'mixins';
@import 'base';
@import 'components/header';
@import 'components/footer';
@import 'components/product-card';
@import 'pages/home';
@import 'pages/product';

// Modern CSS features
.app {
  display: grid;
  grid-template-areas: 
    "header"
    "main"
    "footer";
  min-height: 100vh;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}
```

```javascript
/* static/js/src/app.js */
import { ProductCard } from './components/ProductCard.js';
import { ShoppingCart } from './components/ShoppingCart.js';

class App {
    constructor() {
        this.cart = new ShoppingCart();
        this.initializeComponents();
    }
    
    async initializeComponents() {
        const productCards = document.querySelectorAll('.product-card');
        productCards.forEach(card => {
            new ProductCard(card, this.cart);
        });
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new App();
});
```

## Configuration-Based Setup

### YAML Configuration

Using YAML files to define bundles:

```yaml
# assets.yml
css_main:
  contents:
    - css/normalize.css
    - css/base.css
    - css/layout.css
    - css/components.css
  filters: cssmin
  output: dist/main.min.css

css_admin:
  contents:
    - admin/css/admin.css
    - admin/css/dashboard.css
    - admin/css/forms.css
  filters: cssmin
  output: admin/admin.min.css

js_app:
  contents:
    - js/vendor/jquery.js
    - js/vendor/vue.js
    - js/app/main.js
    - js/app/components/*.js
  filters: jsmin
  output: dist/app.min.js

js_admin:
  contents:
    - admin/js/admin.js
    - admin/js/charts.js
    - admin/js/forms.js
  filters: jsmin
  output: admin/admin.min.js
```

```python
# app.py
from quart import Quart
from quart_assets import QuartAssets

app = Quart(__name__)
assets = QuartAssets(app)

# Load bundles from YAML
assets.from_yaml('assets.yml')

# Or load from Python module
# assets.from_module('config.bundles')
```

### Environment-Specific Configuration

```python
# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
class DevelopmentConfig(Config):
    DEBUG = True
    ASSETS_DEBUG = True
    ASSETS_AUTO_BUILD = True
    ASSETS_CACHE = False

class ProductionConfig(Config):
    DEBUG = False
    ASSETS_DEBUG = False
    ASSETS_AUTO_BUILD = True
    ASSETS_CACHE = True
    ASSETS_URL_EXPIRE = True

class TestingConfig(Config):
    TESTING = True
    ASSETS_DEBUG = True
    ASSETS_AUTO_BUILD = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
```

```python
# app.py
import os
from quart import Quart
from quart_assets import QuartAssets
from config import config

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('QUART_ENV', 'default')
    
    app = Quart(__name__)
    app.config.from_object(config[config_name])
    
    assets = QuartAssets(app)
    assets.from_yaml('assets.yml')
    
    return app
```

## Production Deployment

### Docker Setup

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy source code
COPY . .

# Build assets for production
ENV QUART_ENV=production
RUN python -m quart assets build

# Run the application
CMD ["gunicorn", "-k", "quart.worker.QuartWorker", "app:app"]
```

### Nginx Configuration

```nginx
# nginx.conf
server {
    listen 80;
    server_name example.com;

    # Serve static assets directly
    location /static/ {
        alias /app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Serve asset bundles with aggressive caching
    location /static/dist/ {
        alias /app/static/dist/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        gzip on;
        gzip_types text/css application/javascript;
    }

    # Proxy to Quart application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Testing Assets

### Test Configuration

```python
# tests/conftest.py
import pytest
from quart import Quart
from quart_assets import QuartAssets

@pytest.fixture
def app():
    app = Quart(__name__)
    app.config['TESTING'] = True
    app.config['ASSETS_DEBUG'] = True
    app.config['ASSETS_AUTO_BUILD'] = False
    
    assets = QuartAssets(app)
    assets.from_yaml('assets.yml')
    
    return app

@pytest.fixture
def client(app):
    return app.test_client()
```

### Asset Tests

```python
# tests/test_assets.py
import pytest
from quart_assets import QuartAssets, Bundle

def test_bundle_registration(app):
    assets = app.jinja_env.assets_environment
    
    # Test bundle exists
    assert 'css_main' in assets
    assert 'js_app' in assets
    
    # Test bundle contents
    css_bundle = assets['css_main']
    assert css_bundle.output == 'dist/main.min.css'

@pytest.mark.asyncio
async def test_asset_urls_in_template(client):
    response = await client.get('/')
    
    # Check that asset URLs are present
    assert b'/static/dist/main.min.css' in response.data
    assert b'/static/dist/app.min.js' in response.data
```

## Performance Optimization

### Asset Compression

```python
# app.py - Production optimization
from quart import Quart
from quart_assets import QuartAssets, Bundle

app = Quart(__name__)
assets = QuartAssets(app)

# Aggressive compression for production
if not app.debug:
    # CSS with maximum compression
    css_bundle = Bundle(
        'scss/main.scss',
        filters='pyscss,cssmin',
        output='dist/app.min.css'
    )
    
    # JavaScript with modern optimization
    js_bundle = Bundle(
        'js/src/*.js',
        filters=['babel', 'jsmin'],
        output='dist/app.min.js'
    )
    
    # Set cache-busting
    app.config['ASSETS_URL_EXPIRE'] = True
    app.config['ASSETS_CACHE'] = '/tmp/webassets-cache'
```

### CDN Integration

```python
# config.py - CDN configuration
class ProductionConfig(Config):
    ASSETS_URL = 'https://cdn.example.com/static'
    ASSETS_DEBUG = False
    ASSETS_AUTO_BUILD = True
    ASSETS_URL_EXPIRE = True
```

These examples demonstrate various ways to integrate Quart-Assets into your
applications, from simple single-file apps to complex multi-blueprint
applications with modern build tooling.
