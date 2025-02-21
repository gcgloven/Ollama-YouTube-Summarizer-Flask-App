# youtube_summarizer/utils/ollama_client.py
from ollama import Client, ListResponse

OLLAMA_HOST = "http://127.0.0.1:11434"

AI = Client(host=OLLAMA_HOST)

def getAvailableModels():
    try:
        resp: ListResponse = AI.list()
        return [m.model for m in resp.models]
    except Exception as e:
        print("Error listing Ollama models:", e)
        return []
