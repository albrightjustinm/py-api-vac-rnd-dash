"""Main application and routing logic for Vaccine R&D Dash API."""
from decouple import config
from flask import Flask, json, jsonify, request
from api.routes.mock_routes import mock_routes
from flask_cors import CORS
from flask_caching import Cache

# Custom errors
from errors import InvalidUsage

# Logging
import logging

###########
###Setup###
###########
# Local Environment Testing Only.
#   Un-comment to build enviorment script in instance folder.
# from instance import setup
# setup.setup_env()


# Set database name
local_db_name = 'test.sqlite3'  # Change this or override with config.py file in instance/

def create_app(test_config=None):
    """
    Creates app
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DEBUG=config('DEBUG', default=False),  # Make sure to change debug to False in production env
        SECRET_KEY=config('SECRET_KEY', default='dev'),  # CHANGE THIS!!!!
        DATABASE_URI=config('DATABASE_URI', 'sqlite:///' + os.path.join(os.getcwd(), local_db_name)),  # For in-memory db: default='sqlite:///:memory:'),
        LOGFILE=config('LOGFILE', os.path.join(app.instance_path, 'logs/debug.log')),
        CACHE_TYPE=config('CACHE_TYPE', 'simple'),  # Configure caching
        CACHE_DEFAULT_TIMEOUT=config('CACHE_DEFAULT_TIMEOUT', 300), # Long cache times probably ok for ML api
    )
    # Enable CORS header support
    CORS(app)

    # Enable caching
    cache = Cache(app)

    # Register routes
    app.register_blueprint(mock_routes)

    return app
