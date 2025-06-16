# Environment API

The `QuartAssets` class is the main entry point for integrating webassets with your Quart application.

## QuartAssets

::: quart_assets.QuartAssets
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

## Configuration Storage

The configuration storage classes handle how webassets configuration is stored
and accessed within Quart applications.

### QuartConfigStorage

::: quart_assets.extension.QuartConfigStorage
    options:
      show_root_heading: true
      show_source: true
      heading_level: 4

## Resolvers

Resolvers handle how asset files are located and how URLs are generated for them.

### QuartResolver

::: quart_assets.extension.QuartResolver
    options:
      show_root_heading: true
      show_source: true
      heading_level: 4

## Jinja2 Integration

Custom filters and extensions for Jinja2 template integration.

### Jinja2Filter

::: quart_assets.extension.Jinja2Filter
    options:
      show_root_heading: true
      show_source: true
      heading_level: 4

### AsyncAssetsExtension

::: quart_assets.extension.AsyncAssetsExtension
    options:
      show_root_heading: true
      show_source: true
      heading_level: 4

## Utility Functions

### get_static_folder

::: quart_assets.extension.get_static_folder
    options:
      show_root_heading: true
      show_source: true
      heading_level: 4
