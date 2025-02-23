# 🎥 Local Ollama YouTube Video Summarizer 
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-%23000.svg?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)

Build a YouTube video summarizer using Flask and Ollama AI, running 100% on your local machine. Get concise video summaries without relying on cloud services or API keys. Perfect for privacy-conscious users who want fast, AI-powered insights from any YouTube video!"

(99.9% generated code, prompt, README, 0.01% human effort for copy-pasting)


![App Screenshot](https://i.imgur.com/hty0wiI.png)

## ✨ Key Features

- 🤖 **100% Local AI Processing** - Uses Ollama for local LLM inference
- 🎯 **Dual Transcription** - YouTube API + Local Whisper fallback
- 📝 **Custom Summary Prompts** - Personalize your summary style
- 🔄 **Real-time Token Streaming** - Watch summaries generate live
- 💾 **Full CRUD Operations** - Manage your summaries and prompts
- 📱 **Responsive UI** - Works great on desktop and mobile

## 🛠️ Tech Stack

- **Backend Framework:** Flask
- **AI/ML:**
  - Ollama (Local LLM Server)
  - OpenAI Whisper (Local Speech-to-Text)
- **APIs & Libraries:**
  - youtube-transcript-api
  - yt-dlp
  - SSE (Server-Sent Events)
- **Frontend:**
  - Vanilla JavaScript
  - HTML/CSS
  - Bootstrap

## 📋 Prerequisites

- Python 3.10+
- [Ollama](https://github.com/jmorganca/ollama) server running locally
- ffmpeg (for audio processing)

## 🚀 Quick Start

1. **Clone and Setup:**
```bash
git clone https://github.com/yourusername/youtube-summarizer
cd youtube-summarizer
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
```

2. **Install Dependencies:**
```bash
pip install flask yt_dlp openai-whisper youtube_transcript_api ollama markdown
```

3. **Start Ollama & Install Models:**
```bash
ollama run qwen2.5:7b    # 7B parameters
ollama run tulu3         # 8B parameters
ollama run deepseek-r1   # 7B parameters
```

4. **Launch the App:**
```bash
python run.py
```

5. **Access the Interface:**
- Open `http://127.0.0.1:5000` in your browser
- Enter a YouTube URL
- Choose your local LLM model
- Click "Stream Summarize"

## 📖 Documentation

### Project Structure
---

## Project Structure
```graphql
youtube_summarizer/
├── run.py                      # Entry point to run the Flask app
├── youtube_summarizer/
│   ├── __init__.py            # Creates the Flask app, registers blueprints
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── main.py            # Home page, SSE logic, streaming
│   │   ├── prompt.py          # Prompt CRUD routes
│   │   └── summary.py         # Summary CRUD routes
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── ollama_client.py   # Ollama client config (host, list models)
│   │   ├── storage.py         # JSON loading/saving for prompts & summaries
│   │   └── transcript.py      # YouTube transcript & Whisper logic
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html         # Main SSE page
│   │   ├── manage_prompts.html
│   │   ├── edit_prompt.html
│   │   ├── edit_summary.html
│   │   └── view_summary.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── main.js        # JavaScript for SSE streaming & UI behaviors
└── cache/
    ├── summaries.json         # Saved summary records
    ├── prompts.json           # Saved prompt records
    └── [transcripts, audio]   # Various cached files

```
### Key directories:
- youtube_summarizer/routes: Each file is a Blueprint handling different parts of the app.
- youtube_summarizer/utils: Helper modules for storing data, calling Ollama, or managing transcripts.
- youtube_summarizer/templates: All HTML templates, separated for maintainability.
- youtube_summarizer/static: Custom JS, CSS, or other static files.
- cache/: Stores JSON data (summaries.json, prompts.json) and downloaded transcripts/audio.


### Key Components

- **Route Handlers:** Organized as Flask blueprints
- **Storage System:** JSON-based for simplicity
- **Transcription:** Dual system with API + local fallback
- **UI:** Real-time updates via SSE streaming

## 🔧 Configuration

```python
# run.py
app.run(debug=True, port=5000)

# youtube_summarizer/utils/ollama_client.py
OLLAMA_HOST = "http://127.0.0.1:11434"

```
Install some example small models based on you PC specs:
``` bash
ollama run qwen2.5:7b
ollama run tulu3 #8B
ollama run deepseek-r1 #7B
```

## ❓ FAQ

1. **Why can't I get transcripts?**
   - YouTube transcripts might be disabled or unavailable
   - The app will automatically fall back to Whisper
   - If both fail, verify your ffmpeg and whisper installations

2. **How do I add more LLM models?**
   - Use Ollama's pull command: `ollama pull llama2-7b`
   - Restart the Ollama server
   - The new model will appear in the dropdown list

3. **Why do I see weird spacing in streaming tokens?**
   - This is normal for real-time token streaming
   - The final text is properly formatted in the backend
   - For cleaner text, you can format the summary after completion

4. **Can I enable Markdown in summaries?**
   - Yes! Install the markdown package: `pip install markdown`
   - Parse in your route: `record["summary"]`
   - Display in template: `{{ summary_html|safe }}`

5. **Why are generated titles sometimes quirky?**
   - Titles are LLM-generated
   - You can customize the output by adjusting the `title_prompt`
   - Consider fine-tuning the prompt for better results
   
## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

## 🌟 Show Your Support

Give a ⭐️ if this project helped you!

## FAQ

## 📫 Contact

Your Name - [@WhiteWolfBay](https://closeai.com/)

Project Link: [https://github.com/gcgloven/OllamaYouTubeSummarizerFlaskApp](https://github.com/gcgloven/OllamaYouTubeSummarizerFlaskApp)
