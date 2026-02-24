import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are a friendly voice assistant on Windows 11 named KajuAI.
You talk briefly and clearly. If the user asks to do something on the laptop,
respond with a short confirmation and what you did. If it's normal chat, respond naturally.
"""

# Keep short memory
history = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

def chat_reply(user_text: str) -> str:
    history.append({"role": "user", "content": user_text})

    # Using Chat Completions (simple). (Responses API also exists.) :contentReference[oaicite:2]{index=2}
    resp = client.chat.completions.create(
        model="gpt-5",  # if your account doesn't have it, use another available model in your dashboard
        messages=history,
        temperature=0.6,
    )

    reply = resp.choices[0].message.content.strip()
    history.append({"role": "assistant", "content": reply})

    # limit memory
    if len(history) > 12:
        history[:] = [history[0]] + history[-10:]

    return reply