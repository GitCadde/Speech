import requests
from texttospeech import speak
from config import weatherkey, gnews_key
from gptcalls import ask_chat_gpt
import urllib.request
import json
import requests
from bs4 import BeautifulSoup
import youtube_dl
from moviepy.editor import *
from pydub import AudioSegment
from pydub.playback import play
import tempfile


def check_commands(text):
    commands = [
        ("Wetter" in text and "heute" in text, show_weather),
    ]
    
    for condition, function in commands:
        if condition:
            # Ausführen der zugehörigen Funktion
            function()
            return True
    
    return False

def show_weather():
    url = f"https://api.openweathermap.org/data/2.5/weather?q=Wolfsburg&units=metric&appid={weatherkey}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        temp = data['main']['temp']
        weather = data['weather'][0]['description']
        weather_response = f"Aktuelles Wetter in Wolfsburg: {weather}. Die Temperatur beträgt {round(temp, 1)} Grad Celsius."
        speak(weather_response)
    else:
        speak("Entschuldigung, ich konnte das Wetter nicht abrufen.")
