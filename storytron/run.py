#!/usr/bin/env python3
"""
StoryTRON Flask Application Runner
"""
import argparse
from app import app

if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run the StoryTRON Flask application')
    parser.add_argument('--debug', action='store_true',
                       help='Run in debug mode with auto-reload')
    args = parser.parse_args()

    print(f"Starting StoryTRON on {app.config['HOST']}:{app.config['PORT']}")

    # Check OpenAI API key
    openai_api_key = app.config.get('OPENAI_API_KEY')
    if openai_api_key:
        masked_key = f"{openai_api_key[:12]}...{openai_api_key[-8:]}"
        print(f"OpenAI API Key: {masked_key}")
    else:
        print("OpenAI API Key: NOT SET!")

    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=args.debug
    )
