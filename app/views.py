"""
Handle requests.

Authors:
Majeed Malik
"""

from flask import render_template

def index():
    """Render Startpage."""
    return render_template(
        'index.html'
    )