# import required modules
from logging import exception

import speech_recognition as sr
import pyttsx3
import time
import webbrowser
import music_library
import subprocess
import requests
import os
import wikipedia
import warnings
warnings.filterwarnings("ignore")  # to hide the message
import pywhatkit
import datetime


def send_whatsapp_message(phone, message, delay=2):
    try:
        now = datetime.datetime.now()
        minute = (now.minute + delay) % 60
        hour = now.hour + ((now.minute + delay) // 60)

        pywhatkit.sendwhatmsg(phone, message, hour, minute)
        return f"message scheduled to {phone}"
    except Exception as e:
        return f"Error sending message: {e}"


def get_info(query):
    try:
        # increase number of sentences if you want more information
            summary = wikipedia.summary(query, sentences=5, auto_suggest=False)
            return summary
    except wikipedia.DisambiguationError as e:
            return f"That topic is ambiguous. Try something more specific like: {e.options[0]}"
    except wikipedia.PageError:
            return "Sorry, I couldn’t find information on that topic."
    except Exception as e:
        return f"An error occurred: {e}"

def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source, timeout=3, phrase_time_limit=5)
        print("recognizing...")
        try:

            text = r.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except:
            return ""

def speak(text):
    print(f"Iris : {text}")
    engine = pyttsx3.init()  # re-init every time
    voices = engine.getProperty('voices') 
    engine.setProperty('voice', voices[1].id)  # change number for another voice
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1.0)
    engine.say(text)
    engine.runAndWait()


def get_weather(city):
    api_key = "YOUR_API_KEY"
    base_url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }

    try:
        response = requests.get(base_url, params=params)
        data = response.json()

        if str(data["cod"]) != "200":
            return f"Couldn't find weather for {city}. Please try again."

        weather = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]

        return f"The weather in {city} is {weather} with a temperature of {temp}°C, feels like {feels_like}°C."

    except Exception as e:
        return f"Error fetching weather: {e}"

def process_command(c): # main function for adding commands for Iris

    c = c.lower()
    if 'open' in c:
        time.sleep(1)  # give TTS time to finish
        site = c.replace('open', '').strip()
        url = f'https://{site}.com'
        webbrowser.open(url)
    elif 'open notepad' in c:
        os.system('Notepad')
    elif c.startswith('play'):
        songs = c.split(' ')[1]
        link = music_library.music[songs]
        webbrowser.open(link)
    elif 'weather' in c.lower():
        speak("Sure, please tell me the city name.")
        time.sleep(1)
        city = take_command().lower()
        if city:
            report = get_weather(city)
            speak(report)
        else:
            speak("I didn’t catch the city name.")
    elif 'tell me about' in c:
        topic = c.replace('tell me about', '').strip()
        speak("getting information...")
        info = get_info(topic)
        speak(info)

    elif "send message" in c.lower():
        speak("who should I send it to?")
        contact = take_command().lower()

        contacts = {
            'mom': "+123456789",
            'sister': '+123456789'
        }
        if contact in contacts:
            speak('what should I say?')
            message = take_command()
            report = send_whatsapp_message(contacts[contact], message)
            speak(report)
        else:
            speak('I do not have that contact yet')



def main():
    wakeWord = 'iris'
    speak("Initializing Iris...")

    while True:
        r = sr.Recognizer()  # <-- recreate recognizer every loop
        with sr.Microphone() as source:
            print("Listening...")
            try:
                audio = r.listen(source, timeout=2, phrase_time_limit=2)
                print("Recognizing...")
                word = r.recognize_google(audio)
                print(word)

                if wakeWord in word.lower():
                    time.sleep(0.5)
                    speak("Yes")

                    # listen for command
                    with sr.Microphone() as source:
                        print("Iris active...")
                        r.adjust_for_ambient_noise(source)
                        audio_cmd = r.listen(source, timeout=3, phrase_time_limit=5)
                        command = r.recognize_google(audio_cmd)
                        print(f"Command: {command}")
                        process_command(command)

            except sr.WaitTimeoutError:
                print("No speech detected.")
            except sr.UnknownValueError:
                print("Could not understand audio.")
            except Exception as e:
                print(f"Error: {e}")

        time.sleep(1)  # give the mic a short rest before next listen

if __name__ == "__main__":
    main()
