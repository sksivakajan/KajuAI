from config import MODE
from speech.tts import speak
from speech.stt_online import listen_online
from speech.stt_offline import listen_offline
from commands import run_command, smart_parse  # make sure smart_parse exists in commands.py
from chatgpt_brain import chat_reply


def listen_auto():
    if MODE == "online":
        return listen_online()
    if MODE == "offline":
        return listen_offline()
    t = listen_online()
    if t == "__ONLINE_FAILED__":
        return listen_offline()
    return t


def normalize(text: str) -> str:
    return " ".join((text or "").lower().strip().split())


def looks_like_action(text: str) -> bool:
    # if smart_parse will create actions like open/search/whatsapp/etc
    # we treat it as an action command
    actions = smart_parse(text)
    return any(a[0] in ("open", "search", "whatsapp", "shutdown", "restart", "lock") for a in actions)


def main():
    speak("Assistant started. Talk to me.")

    while True:
        text = normalize(listen_auto())
        if not text:
            continue

        # If user says "exit"
        if text in ["exit", "quit", "stop"]:
            speak("Goodbye.")
            break

        try:
            # If it looks like an action, run it
            if looks_like_action(text):
                run_command(text)
            else:
                # Otherwise: normal conversation like ChatGPT
                reply = chat_reply(text)
                speak(reply)

        except KeyboardInterrupt:
            break
        except Exception as e:
            speak(f"Sorry, error: {e}")


if __name__ == "__main__":
    main()