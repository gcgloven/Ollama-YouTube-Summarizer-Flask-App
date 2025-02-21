# youtube_summarizer/__init__.py
import os
from flask import Flask

def create_app():
    app = Flask(__name__)

    # Ensure 'cache' folder exists, for transcripts and JSON data
    CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', 'cache')
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    # Register blueprints
    from youtube_summarizer.routes.main import main_bp
    from youtube_summarizer.routes.prompt import prompt_bp
    from youtube_summarizer.routes.summary import summary_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(prompt_bp, url_prefix="/prompts")
    app.register_blueprint(summary_bp)

    return app