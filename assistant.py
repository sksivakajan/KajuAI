import time

from config import MODE
from speech.tts import speak
from speech.stt_online import listen_online
from speech.stt_offline import listen_offline
from commands import run_actions_from_text, is_action_text
from chatgpt_brain import chat_reply


def should_suppress_chat_reply(reply: str) -> bool:
    r = (reply or "").lower()
    blockers = [
        "chat authentication failed",
        "chat is not configured",
        "chat request failed",
        "chat service is unreachable",
        "chat service is temporarily unavailable",
        "chat service returned an invalid response",
    ]
    return any(b in r for b in blockers)


def listen_auto():
    if MODE == "online":
        return listen_online()
    if MODE == "offline":
        return listen_offline()

    # auto: try online then fallback offline
    t = listen_online()
    if t == "__ONLINE_FAILED__":
        return listen_offline()
    return t


def normalize(text: str) -> str:
    return " ".join((text or "").lower().strip().split())


def main():
    speak("Assistant started. Talk to me.")
    last_text = ""
    last_text_at = 0.0

    while True:
        text = normalize(listen_auto())
        if not text:
            continue

        # Ignore duplicate recognition bursts from STT (prevents double open).
        now = time.time()
        if text == last_text and (now - last_text_at) < 3.0:
            continue
        last_text = text
        last_text_at = now

        # Stop words
        if text in ["exit", "quit", "stop"]:
            speak("Goodbye.")
            break

        try:
            # If user said an action sentence, do actions
            if is_action_text(text):
                handled = run_actions_from_text(text)
                if not handled:
                    # if not handled as action, treat as chat
                    reply = chat_reply(text)
                    if not should_suppress_chat_reply(reply):
                        speak(reply)
            else:
                # Normal chat -> ChatGPT reply
                reply = chat_reply(text)
                if not should_suppress_chat_reply(reply):
                    speak(reply)

        except Exception as e:
            speak(f"Sorry, error: {e}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAssistant stopped.")
