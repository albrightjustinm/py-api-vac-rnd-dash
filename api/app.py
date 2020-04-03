"""Main application and routing logic for Vaccine R&D Dash API."""
from flask import Flask, json, jsonify, request
from api.routes.mock_routes import mock_routes
from api.routes.admin_routes import admin_routes
from api.routes.covid_dash import covid_dash
from flask_cors import CORS
from flask_caching import Cache
from decouple import config
import os

# Logging
import logging

###########
###Setup###
###########
# Local Environment Testing Only.
#   Un-comment to build environment script in config.py
# from instance import setup
# setup.setup_env(testing=True)


# Set database name
# Change this or override with config.py file in instance/
local_db_name = 'test.sqlite3'


def create_app(test_config=None):
    """
    Creates app
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # Make sure to change debug to False in production env
        DEBUG=config('DEBUG', default=False),
        SECRET_KEY=config('SECRET_KEY', default='dev'),  # CHANGE THIS!!!!
        # For in-memory db: default='sqlite:///:memory:'),
        DATABASE_URI=config('DATABASE_URI', 'sqlite:///' + \
                            os.path.join(os.getcwd(), local_db_name)),
        LOGFILE=config('LOGFILE', os.path.join(
            app.instance_path, 'logs/debug.log')),
        CACHE_TYPE=config('CACHE_TYPE', 'simple'),  # Configure caching
        # Long cache times probably ok for ML api
        CACHE_DEFAULT_TIMEOUT=config('CACHE_DEFAULT_TIMEOUT', 300),
        TESTING=config('TESTING', default='TRUE')
    )

    # Enable CORS header support
    CORS(app)

    # Enable caching
    cache = Cache(app)

    
    ##############
    ### Routes ###
    ##############
    app.register_blueprint(mock_routes)
    app.register_blueprint(admin_routes)
    app.register_blueprint(covid_dash)

    #############
    ###Logging###
    #############
    # Change logging.INFO to logging.DEBUG to get full logs.  Will be a crapload of information.
    # May significantly impair performance if writing logfile to disk (or network drive).
    # To enable different services, see README.md
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers

    # File logging. Remove in PROD
    if app.config['TESTING'] == 'TRUE':
        logging.basicConfig(filename=app.config['LOGFILE'], level=logging.INFO)
    
    logging.getLogger('flask_cors').level = logging.INFO
    app_logger = logging.getLogger(__name__)

    # Register database functions.  Will allow db.close() to run on teardown
    from api import db
    db.init_app(app)

    return app
