#!/usr/bin/env python
import sys
from os import path

from quart import Quart, render_template
from quart.wrappers import Response
from quart_assets import QuartAssets

sys.path.insert(0, path.join(path.dirname(__file__), "../src"))

app = Quart(__name__)

assets = QuartAssets(app)
assets.register(
    "main", "style1.css", "style2.css", output="cached.css", filters="cssmin"
)


@app.route("/")
async def index() -> str:
    # Test both sync and async template rendering
    return await render_template("index.html")


@app.route("/sync")
async def index_sync() -> str:
    # Test synchronous rendering as well
    from quart import render_template_string

    template_content = """
    <html><head>
    {% assets "main" %}
    <link rel="stylesheet" href="{{ ASSET_URL }}" type="text/css" />
    {% endassets %}
    </head>
    <body>
    <h1>This should be red (sync).</h1>
    <h2>This should be blue (sync).</h2>
    </body>
    """
    return await render_template_string(template_content)


app.run(debug=True)
