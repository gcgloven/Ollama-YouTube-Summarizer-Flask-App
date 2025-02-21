# youtube_summarizer/utils/transcript.py
import os
import yt_dlp
import whisper
from youtube_transcript_api import (
    YouTubeTranscriptApi, TranscriptsDisabled,
    NoTranscriptFound, NoTranscriptAvailable
)
from youtube_summarizer.utils.storage import load_json, save_json

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "cache")

def getVideoID(url: str) -> str:
    if "watch?v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("/")[-1]
    raise ValueError("Unsupported YouTube URL format.")

def get_transcription(video_id: str) -> list:
    """Official YouTube transcript (English)."""
    return YouTubeTranscriptApi.get_transcript(video_id)

def download_audio(url: str, output_path: str) -> str:
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path + '.%(ext)s',
        'quiet': True,
        'noprogress': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    for ext in ['m4a', 'mp3', 'webm', 'aac', 'wav', 'ogg', 'opus']:
        f = f"{output_path}.{ext}"
        if os.path.exists(f):
            return f
    raise FileNotFoundError("Audio not found after download.")

def whisper_transcribe_audio(audio_path: str) -> list:
    model = whisper.load_model("base")  # or "tiny", "small", ...
    result = model.transcribe(audio_path)
    transcripts = []
    for seg in result["segments"]:
        transcripts.append({
            "text": seg["text"],
            "start": seg["start"],
            "duration": seg["end"] - seg["start"]
        })
    return transcripts

def load_or_create_transcript(url: str):
    video_id = getVideoID(url)
    youtube_transcript_path = os.path.join(CACHE_DIR, f"{video_id}_youtube_transcript.json")
    whisper_transcript_path = os.path.join(CACHE_DIR, f"{video_id}_whisper_transcript.json")
    audio_file_path = os.path.join(CACHE_DIR, f"{video_id}_downloaded_audio")

    # 1) Official transcript?
    if os.path.exists(youtube_transcript_path):
        return load_json(youtube_transcript_path)
    else:
        try:
            t = get_transcription(video_id)
            save_json(youtube_transcript_path, t)
            return t
        except (TranscriptsDisabled, NoTranscriptFound, NoTranscriptAvailable):
            pass
        except Exception as e:
            print("Error retrieving official transcript:", e)

    # 2) Fallback to Whisper
    if os.path.exists(whisper_transcript_path):
        return load_json(whisper_transcript_path)
    else:
        # check audio
        final_audio = None
        for ext in ['m4a', 'mp3', 'webm', 'aac', 'wav', 'ogg', 'opus']:
            c = f"{audio_file_path}.{ext}"
            if os.path.exists(c):
                final_audio = c
                break
        if not final_audio:
            final_audio = download_audio(url, audio_file_path)
        try:
            t = whisper_transcribe_audio(final_audio)
            save_json(whisper_transcript_path, t)
            return t
        except Exception as e:
            print("Whisper transcription failed:", e)
            return None
