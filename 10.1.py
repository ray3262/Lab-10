import json
import queue
import sounddevice as sd
import vosk
import pyttsx3
import requests
import sys
import time


def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def recognize_speech():
    model = vosk.Model(r"C:\Users\ray\OneDrive\Desktop\vosk-model-small-ru-0.22")  

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
                speak("Не удалось распознать речь. Попробуйте ещё раз.")
                return ""


def get_activity():
    try:
        response = requests.get("https://www.boredapi.com/api/activity")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Ошибка при получении данных")
    except Exception as e:
        speak("Не удалось получить данные. Проверьте подключение к интернету.")
        return None


def process_command(command, activity):
    command = command.lower()
    
    if "случайный" in command or "следующая" in command:
        activity.update(get_activity() or {})
        speak(f"Попробуйте: {activity.get('activity', 'Не удалось загрузить занятие')}")
    elif "название" in command:
        speak(f"Название: {activity.get('activity', 'Неизвестно')}")
    elif "участники" in command:
        speak(f"Необходимо участников: {activity.get('participants', 'Неизвестно')}")
    elif "сохранить" in command:
        with open("activity.txt", "w", encoding="utf-8") as file:
            json.dump(activity, file, ensure_ascii=False, indent=4)
        speak("Занятие сохранено в файл.")
    elif "стоп" in command:
        speak("Работа завершена. До свидания!")
        exit()
    else:
        speak("Команда не распознана. Попробуйте снова.")

if __name__ == "__main__":
    speak("Голосовой ассистент активирован. Произнесите команду.")
    activity = get_activity() or {}
    while True:
        time.sleep(7)  
        command = recognize_speech()
        if command:
            process_command(command, activity)
        else:
            speak("Не распознана команда. Попробуйте снова.")
