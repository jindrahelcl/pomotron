#!/usr/bin/env python3
"""
StoryTRON Flask Application Runner
"""
from app import app

if __name__ == '__main__':
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
        debug=False
    )
