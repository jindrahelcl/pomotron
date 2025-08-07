#!/usr/bin/env python3
"""
StoryTRON Flask Application Runner
"""
import os
from dotenv import load_dotenv
from app import app
from config import config

# Load environment variables from .env file
load_dotenv()

if __name__ == '__main__':
    # Get configuration environment
    config_name = os.environ.get('FLASK_ENV', 'development')
    app_config = config.get(config_name, config['default'])

    # Configure the app
    app.config.from_object(app_config)

    print(f"Starting StoryTRON on {app_config.HOST}:{app_config.PORT}")
    print(f"Environment: {config_name}")
    print(f"Debug mode: {app_config.DEBUG}")

    app.run(
        host=app_config.HOST,
        port=app_config.PORT,
        debug=app_config.DEBUG
    )
