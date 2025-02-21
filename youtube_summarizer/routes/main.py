# youtube_summarizer/routes/main.py
import math
from flask import Blueprint, render_template, request, Response
from youtube_summarizer.utils.storage import (
    load_summaries, save_summaries, load_prompts, get_next_id,
    ensure_default_prompt_exists
)
from youtube_summarizer.utils.ollama_client import AI, getAvailableModels
from youtube_summarizer.utils.transcript import load_or_create_transcript

from datetime import datetime
import os

main_bp = Blueprint("main_bp", __name__)

@main_bp.route("/")
def index():
    # Ensure we have a default prompt created
    ensure_default_prompt_exists()

    # Handle pagination
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 10))

    all_summaries = load_summaries()
    total = len(all_summaries)

    # Slice the summaries for the current page
    start = (page - 1) * size
    end = start + size
    summaries = all_summaries[start:end]

    models = getAvailableModels()
    prompts = load_prompts()

    return render_template(
        "index.html",
        summaries=summaries,
        model_names=models,
        prompts=prompts,
        page=page,
        size=size,
        total=total
    )

###############################################################################
# SSE logic for new summary creation
###############################################################################
def stream_summary_and_title(url: str, model_name: str, prompt_text: str):
    """
    Generator that:
     1. Loads/creates a transcript
     2. Streams partial tokens for a summary
     3. Then streams partial tokens for a title
     4. Yields 'DONE' and returns summary/title
    """
    transcript = load_or_create_transcript(url)
    if not transcript:
        # yield an error event
        yield "event: ERROR\ndata: Could not get transcripts.\n\n"
        return None, None

    transcript_text = " ".join(seg["text"] for seg in transcript)

    # Build prompts
    summary_prompt = (
        f"{prompt_text}\n\n"
        f"Below is the transcription of the YouTube video.\n"
        f"Generate a concise summary:\n\n{transcript_text}\n\nSUMMARY:\n"
    )
    title_prompt = (
                    f"Below is the transcription of the YouTube video.\n"
                    f"Generate a **short, catchy title** with **exactly 5 to 10 words**. "
                    f"Do **not** exceed 10 words. Do **not** rephrase the entire transcript.\n\n"
                    f"{transcript_text}\n\n"
                    "Strictly output only the title, nothing else:\n"
                )

    # 1) SUMMARY
    summary_builder = []
    try:
        for chunk in AI.generate(prompt=summary_prompt, model=model_name, stream=True):
            token = chunk.get("response", "")
            summary_builder.append(token)
            yield f"event: SUMMARY_CHUNK\ndata: {token}\n\n"
    except Exception as e:
        yield f"event: ERROR\ndata: Summarization error: {str(e)}\n\n"
        return None, None

    full_summary = "".join(summary_builder)

    # 2) TITLE
    title_builder = []
    try:
        for chunk in AI.generate(prompt=title_prompt, model=model_name, stream=True):
            token = chunk.get("response", "")
            title_builder.append(token)
            yield f"event: TITLE_CHUNK\ndata: {token}\n\n"
    except Exception as e:
        yield f"event: ERROR\ndata: Title generation error: {str(e)}\n\n"
        return full_summary, None

    full_title = "".join(title_builder)

    # Done
    yield "event: DONE\ndata: ok\n\n"

    return full_summary.strip(), full_title.strip()

@main_bp.route("/api/summarize_stream", methods=["POST"])
def api_summarize_stream():
    """
    Receives JSON { url, model, prompt_id }, streams SSE to the client,
    and then saves the record once everything is done.
    """
    from flask import jsonify
    data = request.get_json(force=True)
    url = data.get("url")
    model_name = data.get("model")
    prompt_id = int(data.get("prompt_id"))

    # Load the chosen prompt
    prompts = load_prompts()
    prompt_obj = next((p for p in prompts if p["id"] == prompt_id), None)
    if not prompt_obj:
        # fallback to default if not found
        prompt_obj = prompts[0]
    prompt_text = prompt_obj["content"]

    def sse_generator():
        summary_text, title_text = None, None
        gen = stream_summary_and_title(url, model_name, prompt_text)

        returned = None
        try:
            returned = next(gen)
            while True:
                yield returned
                returned = next(gen)
        except StopIteration as stop:
            # The generator's return value is in stop.value (summary_text, title_text)
            summary_text, title_text = stop.value or (None, None)
        except Exception as e:
            yield f"event: ERROR\ndata: {str(e)}\n\n"

        # If we have summary/title, store it
        if summary_text and title_text:
            summaries = load_summaries()
            new_record = {
                "id": get_next_id(summaries),
                "timestamp": datetime.now().isoformat(timespec='seconds'),
                "url": url,
                "model": model_name,
                "prompt_id": prompt_obj["id"],
                "prompt_name": prompt_obj["name"],
                "title": title_text,
                "summary": summary_text
            }
            summaries.append(new_record)
            save_summaries(summaries)

    return Response(sse_generator(), mimetype='text/event-stream')
