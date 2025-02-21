# youtube_summarizer/utils/storage.py
import os
import json

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "cache")
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

SUMMARIES_JSON_PATH = os.path.join(CACHE_DIR, "summaries.json")
PROMPTS_JSON_PATH   = os.path.join(CACHE_DIR, "prompts.json")

DEFAULT_PROMPT_CONTENT = (
    "You are a summarizing assistant that interprets the content of a YouTube video. "
    "Generate a helpful, concise summary, then provide a short, catchy title."
)

def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_summaries():
    return load_json(SUMMARIES_JSON_PATH)

def save_summaries(data):
    save_json(SUMMARIES_JSON_PATH, data)

def load_prompts():
    return load_json(PROMPTS_JSON_PATH)

def save_prompts(data):
    save_json(PROMPTS_JSON_PATH, data)

def get_next_id(records: list) -> int:
    if not records:
        return 1
    return max(item["id"] for item in records) + 1

def ensure_default_prompt_exists():
    """
    If there's no default (protected) prompt, create one.
    """
    prompts = load_prompts()
    for p in prompts:
        if p.get("protected"):
            return
    # Otherwise, create the default
    prompts.append({
        "id": 1,
        "name": "Default Summarizing Prompt",
        "content": DEFAULT_PROMPT_CONTENT,
        "protected": True
    })
    save_prompts(prompts)
