# youtube_summarizer/routes/summary.py
from flask import Blueprint, render_template, request, redirect, url_for
from datetime import datetime

from youtube_summarizer.utils.storage import (
    load_summaries, save_summaries,
    load_prompts, get_next_id
)
from youtube_summarizer.utils.transcript import load_or_create_transcript
from youtube_summarizer.utils.ollama_client import AI, getAvailableModels

summary_bp = Blueprint("summary_bp", __name__)

@summary_bp.route("/summaries/<int:record_id>")
def view_summary(record_id):
    """
    Dedicated page for a single summary record.
    You can do Markdown rendering here if you want.
    """
    summaries = load_summaries()
    record = next((s for s in summaries if s["id"] == record_id), None)
    if not record:
        return "Not found", 404

    # If you want to parse record["summary"] as Markdown, do so.
    # Example:
    # from markdown import markdown
    # summary_html = markdown(record["summary"])
    # pass summary_html to the template

    return render_template("view_summary.html", record=record)

@summary_bp.route("/delete/<int:record_id>", methods=["GET"])
def delete_summary(record_id):
    summaries = load_summaries()
    new_list = [s for s in summaries if s["id"] != record_id]
    if len(new_list) < len(summaries):
        save_summaries(new_list)
    return redirect(url_for("main_bp.index"))

@summary_bp.route("/edit/<int:record_id>", methods=["GET", "POST"])
def edit_summary(record_id):
    summaries = load_summaries()
    record = next((r for r in summaries if r["id"] == record_id), None)
    if not record:
        return "Record not found", 404

    if request.method == "POST":
        # user clicked "regenerate"
        if request.form.get("action") == "regenerate":
            # Remove old record
            new_summaries = [s for s in summaries if s["id"] != record_id]
            save_summaries(new_summaries)

            url_ = request.form.get("video_url").strip()
            model_name = request.form.get("model_name").strip()
            prompt_id = int(request.form.get("prompt_id"))

            # load prompt
            prompts = load_prompts()
            prompt_obj = next((p for p in prompts if p["id"] == prompt_id), None)
            if not prompt_obj:
                prompt_obj = prompts[0]

            transcript = load_or_create_transcript(url_)
            if not transcript:
                return redirect(url_for("main_bp.index"))

            combined_text = " ".join(seg["text"] for seg in transcript)

            # 2-step approach: summary then title
            summary_prompt = f"{prompt_obj['content']}\n\nThe video text:\n{combined_text}\n\nGive me a summary:\n"
            summary_builder = []
            for chunk in AI.generate(prompt=summary_prompt, model=model_name, stream=True):
                summary_builder.append(chunk.get("response", ""))
            full_summary = "".join(summary_builder)

            title_prompt = (
                    f"Below is the transcription of the YouTube video.\n"
                    f"Generate a **short, catchy title** with **exactly 5 to 10 words**. "
                    f"Do **not** exceed 10 words. Do **not** rephrase the entire transcript.\n\n"
                    f"{combined_text}\n\n"
                    "Strictly output only the title, nothing else:\n"
                )
            #f"{prompt_obj['content']}\n\nThe video text:\n{combined_text}\n\nGive me a short title:\n"
            title_builder = []
            for chunk in AI.generate(prompt=title_prompt, model=model_name, stream=True):
                title_builder.append(chunk.get("response", ""))
            full_title = "".join(title_builder)

            # Re-insert record
            final_list = load_summaries()
            new_record = {
                "id": get_next_id(final_list),
                "timestamp": datetime.now().isoformat(timespec='seconds'),
                "url": url_,
                "model": model_name,
                "prompt_id": prompt_id,
                "prompt_name": prompt_obj["name"],
                "title": full_title.strip(),
                "summary": full_summary.strip()
            }
            final_list.append(new_record)
            save_summaries(final_list)

        return redirect(url_for("main_bp.index"))
    else:
        # GET: show the form
        model_names = getAvailableModels()
        prompts = load_prompts()
        return render_template("edit_summary.html",
                               record=record,
                               model_names=model_names,
                               prompts=prompts)
