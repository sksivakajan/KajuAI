import os
import requests

# Set in PowerShell (current terminal):
#   $env:HF_TOKEN="hf_xxx"
# Or permanent:
#   setx HF_TOKEN "hf_xxx"
HF_TOKEN = os.environ.get("HF_TOKEN")

MODEL_ID = "microsoft/Phi-3-mini-4k-instruct"

# Hugging Face router endpoint (replaces api-inference.huggingface.co)
API_URL = f"https://router.huggingface.co/hf-inference/models/{MODEL_ID}"

SYSTEM_PROMPT = "You are a friendly Windows voice assistant. Reply briefly and clearly for voice."


def chat_reply(user_text: str) -> str:
    if not HF_TOKEN:
        return "Chat is not configured. Set HF_TOKEN in PowerShell."

    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    prompt = f"{SYSTEM_PROMPT}\n\nUser: {user_text}\nAssistant:"

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 120,
            "temperature": 0.7,
            "return_full_text": False,
        },
    }

    try:
        r = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    except requests.RequestException:
        return "Chat service is unreachable right now. Check your internet connection."

    if r.status_code in (401, 403):
        return "Chat authentication failed. Please update HF_TOKEN."
    if r.status_code >= 500:
        return "Chat service is temporarily unavailable. Try again in a moment."

    try:
        data = r.json()
    except ValueError:
        return "Chat service returned an invalid response. Please try again."

    if isinstance(data, dict) and "error" in data:
        return "Chat request failed. Verify HF_TOKEN and model access."

    if isinstance(data, list) and len(data) > 0:
        return (data[0].get("generated_text") or "").strip()

    return "Sorry, I could not generate a reply right now."
