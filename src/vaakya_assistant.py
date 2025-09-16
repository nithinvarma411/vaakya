import pvporcupine
import sounddevice as sd
import numpy as np
import requests
import queue
import wave
import time
import tempfile
from dotenv import load_dotenv
import os
import pyttsx3  

load_dotenv()

ACCESS_KEY = os.environ["PICOVOICE_ACCESS_KEY"]  

# --------------- Settings ---------------
WAKEWORD = "jarvis"
SILENCE_SEC = 5  # time of silence for end-of-command
MIN_RECORD_SEC = 3
AUDIO_SAMPLE_RATE = 16000
AUDIO_FILENAME = "user_command.wav"
TRANSCRIBE_API = "http://localhost:8000/transcribe"
# -----------------------------------------

def play_tts(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def save_wav(filename, audio, sample_rate):
    audio = np.concatenate(audio)
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio.tobytes())

def record_until_silence(timeout=SILENCE_SEC, min_sec=MIN_RECORD_SEC):
    print("[.] Recording command (speak now)...")
    audio_buffer = []
    silence_buffer = []
    silence_start = None

    def callback(indata, frames, time, status):
        nonlocal audio_buffer, silence_buffer, silence_start
        amplitude = np.abs(indata).mean()
        audio_buffer.append(indata.copy())
        if amplitude < 500:  # threshold: adjust as needed
            silence_buffer.append(indata.copy())
            if silence_start is None:
                silence_start = time.inputBufferAdcTime
        else:
            silence_buffer.clear()
            silence_start = None

    with sd.InputStream(samplerate=AUDIO_SAMPLE_RATE, channels=1, dtype='int16', callback=callback):
        start_time = time.time()
        while True:
            sd.sleep(100)  # check every 100 ms
            if len(audio_buffer) == 0:
                continue
            duration = (len(audio_buffer) * 1024) / AUDIO_SAMPLE_RATE
            if silence_start is not None and (time.time() - start_time) > min_sec:
                # If silence has lasted long enough and at least min_sec has passed
                if (time.time() - silence_start) > timeout:
                    print("[.] Silence detected, ending recording.")
                    break
    save_wav(AUDIO_FILENAME, audio_buffer, AUDIO_SAMPLE_RATE)
    return AUDIO_FILENAME

def listen_for_wakeword():
    porcupine = pvporcupine.create(access_key=ACCESS_KEY, keywords=[WAKEWORD])
    q = queue.Queue()
    def audio_callback(indata, frames, time, status):
        if status: print(status)
        q.put(indata.copy())
    with sd.InputStream(channels=1, samplerate=porcupine.sample_rate, dtype='int16',
                        blocksize=porcupine.frame_length, callback=audio_callback):
        print("[~] Waiting for wake word...")
        while True:
            pcm = q.get().flatten()
            result = porcupine.process(pcm)
            if result >= 0:
                print("[*] Wake word detected!")
                break

def process_user_command():
    # Step 1: TTS prompt
    play_tts("How can I help you?")
    # Step 2: Record command (auto-stop on silence)
    audio_file = record_until_silence()
    # Step 3: Transcribe (call FastAPI backend)
    with open(audio_file, "rb") as f:
        files = {'audio': (AUDIO_FILENAME, f, 'audio/wav')}
        response = requests.post(TRANSCRIBE_API, files=files)
        if response.ok:
            transcription = response.json()["transcription"]
            print("[AI Assistant] Recognized:", transcription)
            # Step 4: Do something smart here
            command = transcription.lower().strip()

            if command.startswith("open "):
                target = command[len("open "):].strip()
                print(f"[AI Assistant] User wants to open: {target}")

                # Handle well-known cases first
                if "youtube" in target:
                    import webbrowser
                    webbrowser.open("https://www.youtube.com")
                    play_tts(f"Opening YouTube.")
                elif "google" in target:
                    import webbrowser
                    webbrowser.open("https://www.google.com")
                    play_tts(f"Opening Google.")
                elif "vs code" in target or "visual studio" in target:
                    import os
                    os.system("code")  # Make sure 'code' is in PATH
                    play_tts("Opening Visual Studio Code.")
                elif "powerpoint" in target or "ppt" in target:
                    import os
                    os.system("start powerpnt")
                    play_tts("Opening PowerPoint.")
                elif "." in target.replace(" ", ""):  # Looks like a domain (e.g., "open github.com")
                    import webbrowser
                    webbrowser.open("https://" + target.replace(" ", ""))
                    play_tts(f"Opening {target}.")
                else:
                    play_tts(f"Sorry, I don't know how to open {target} yet.")
            else:
                # Add other command logic here if needed
                play_tts("You said: " + transcription)
        else:
            print("Transcription failed:", response.text)
            play_tts("Sorry, something went wrong.")

def run_assistant():
    while True:
        listen_for_wakeword()
        print("[*] Jarvis is listening for your commands (multi-turn mode)")
        play_tts("How can I help you?")

        conversation_window_sec = 30
        start_conv = time.time()
        while True:
            audio_file = record_until_silence(timeout=SILENCE_SEC)
            transcription = None
            with open(audio_file, "rb") as f:
                files = {'audio': (AUDIO_FILENAME, f, 'audio/wav')}
                response = requests.post(TRANSCRIBE_API, files=files)
                if response.ok:
                    transcription = response.json()["transcription"]
                    print("[AI Assistant] Recognized:", transcription)
                else:
                    print("Transcription failed:", response.text)
                    play_tts("Sorry, something went wrong.")
                    continue

            if not transcription or not transcription.strip():
                if time.time() - start_conv > conversation_window_sec:
                    play_tts("Going back to sleep. Say 'jarvis' when you need me again.")
                    break
                continue

            command = transcription.lower().strip()

            # Exit if asked
            if any(word in command for word in ["stop", "goodbye", "bye", "exit", "thank you", "thanks", "that's all"]):
                play_tts("Okay, going back to sleep. Just say 'jarvis' when you need me!")
                break

            # Handle "open {something}" dynamically
            if command.startswith("open "):
                target = command[len("open "):].strip()
                print(f"[AI Assistant] User wants to open: {target}")

                if "youtube" in target:
                    import webbrowser
                    webbrowser.open("https://www.youtube.com")
                    play_tts(f"Opening YouTube.")
                elif "google" in target:
                    import webbrowser
                    webbrowser.open("https://www.google.com")
                    play_tts(f"Opening Google.")
                elif "vs code" in target or "visual studio" in target:
                    import os
                    os.system("code")
                    play_tts("Opening Visual Studio Code.")
                elif "powerpoint" in target or "ppt" in target:
                    import os
                    os.system("start powerpnt")
                    play_tts("Opening PowerPoint.")
                elif "." in target.replace(" ", ""):  # e.g. "github.com"
                    import webbrowser
                    webbrowser.open("https://" + target.replace(" ", ""))
                    play_tts(f"Opening {target}.")
                else:
                    play_tts(f"Sorry, I don't know how to open {target} yet.")
            else:
                # Fallback for other commands
                play_tts("You said: " + transcription)

            # Timeout
            if time.time() - start_conv > conversation_window_sec:
                play_tts("Conversation timed out. Say 'jarvis' again when needed.")
                break

        print("Ready for next wake word...")

if __name__ == "__main__":
    run_assistant()
