# youtube_summarizer/routes/prompt.py
from flask import Blueprint, render_template, request, redirect, url_for
from youtube_summarizer.utils.storage import (
    load_prompts, save_prompts,
    ensure_default_prompt_exists,
    get_next_id
)

prompt_bp = Blueprint("prompt_bp", __name__)

@prompt_bp.route("/")
def manage_prompts():
    ensure_default_prompt_exists()
    prompts = load_prompts()
    return render_template("manage_prompts.html", prompts=prompts)

@prompt_bp.route("/new", methods=["POST"])
def prompt_create():
    prompt_name = request.form.get("prompt_name")
    prompt_content = request.form.get("prompt_content")
    if not prompt_name or not prompt_content:
        return redirect(url_for("prompt_bp.manage_prompts"))

    prompts = load_prompts()
    new_prompt = {
        "id": get_next_id(prompts),
        "name": prompt_name.strip(),
        "content": prompt_content.strip(),
        "protected": False
    }
    prompts.append(new_prompt)
    save_prompts(prompts)
    return redirect(url_for("prompt_bp.manage_prompts"))

@prompt_bp.route("/edit/<int:prompt_id>", methods=["GET", "POST"])
def prompt_edit(prompt_id):
    prompts = load_prompts()
    prompt = next((p for p in prompts if p["id"] == prompt_id), None)
    if not prompt:
        return "Prompt not found", 404

    if request.method == "POST":
        if prompt.get("protected"):
            return redirect(url_for("prompt_bp.manage_prompts"))
        # update
        prompt["name"] = request.form.get("prompt_name") or prompt["name"]
        prompt["content"] = request.form.get("prompt_content") or prompt["content"]
        save_prompts(prompts)
        return redirect(url_for("prompt_bp.manage_prompts"))
    else:
        return render_template("edit_prompt.html", prompt=prompt)

@prompt_bp.route("/delete/<int:prompt_id>", methods=["GET"])
def prompt_delete(prompt_id):
    prompts = load_prompts()
    prompt = next((p for p in prompts if p["id"] == prompt_id), None)
    if not prompt:
        return redirect(url_for("prompt_bp.manage_prompts"))
    if prompt.get("protected"):
        return redirect(url_for("prompt_bp.manage_prompts"))  # can't delete default
    new_list = [p for p in prompts if p["id"] != prompt_id]
    save_prompts(new_list)
    return redirect(url_for("prompt_bp.manage_prompts"))
