# run.py
from youtube_summarizer import create_app

app = create_app()

if __name__ == "__main__":
    # Adjust host/port/debug as you like
    app.run(debug=True, port=5000)