"""
Processing of all the calls.

Authors:
Majeed Malik
"""

from flask import Flask, make_response, render_template

def create_app():
    """Create the App."""
    app = Flask(__name__)
    # app.config.from_object(config_class)

    from app import views

    app.register_error_handler(404, handle_client_error)
    app.add_url_rule('/', 'index', views.index)
    app.add_url_rule('/index', 'index', views.index)

    return app

def handle_client_error(exc):
    """Show Error Page."""
    return make_response(render_template('%d.html' % exc.code), exc.code)