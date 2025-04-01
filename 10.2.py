import json
import queue
import sounddevice as sd
import vosk
import pyttsx3
import requests
import webbrowser
import sys

def speak(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for voice in voices:
        if "English" in voice.name:
            engine.setProperty('voice', voice.id)
            break
    engine.say(text)
    engine.runAndWait()

def recognize_speech(model_path):
    model = vosk.Model(model_path)
    q = queue.Queue()
    
    def callback(indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        q.put(bytes(indata))

    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        recognizer = vosk.KaldiRecognizer(model, 16000)
        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                return result.get("text", "")
            else:
                speak("I didn't understand. Try again.")
                return ""

def get_activity():
    try:
        response = requests.get("https://www.boredapi.com/api/activity")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Error fetching data")
    except Exception:
        speak("Failed to get data. Check your internet connection.")
        return None

def get_word_info(word):
    try:
        response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Error fetching word data")
    except Exception:
        speak("Failed to retrieve word information.")
        return None

def process_command(command, activity):
    command = command.lower()
    if "random" in command or "next" in command:
        activity.update(get_activity() or {})
        speak(f"Try this: {activity.get('activity', 'Activity not found')}")
    elif "name" in command:
        speak(f"Activity: {activity.get('activity', 'Unknown')}")
    elif "participants" in command:
        speak(f"Participants needed: {activity.get('participants', 'Unknown')}")
    elif "save" in command:
        with open("activity.txt", "w", encoding="utf-8") as file:
            json.dump(activity, file, ensure_ascii=False, indent=4)
        speak("Activity saved to file.")
    elif "stop" in command:
        speak("Goodbye!")
        exit()
    elif command.startswith("find"):
        word = command.split("find", 1)[-1].strip()
        if word:
            word_info = get_word_info(word)
            if word_info:
                meaning = word_info[0]['meanings'][0]['definitions'][0]['definition']
                speak(f"The meaning of {word} is: {meaning}")
        else:
            speak("Please specify a word to find.")
    elif "link" in command:
        webbrowser.open("https://www.boredapi.com/")
        speak("Opening the link.")
    else:
        speak("Command not recognized. Try again.")

if __name__ == "__main__":
    model_path = r"C:\Users\ray\OneDrive\Desktop\vosk-model-en-us-0.22"
    speak("Voice assistant activated. Say a command.")
    activity = get_activity() or {}
    while True:
        command = recognize_speech(model_path)
        if command:
            process_command(command, activity)
