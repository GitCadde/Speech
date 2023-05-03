from speechtotext import SpeechRecognition
import os

os.system("clear")
JARVIS = SpeechRecognition()

while True:
    try:
        JARVIS.listen_and_transcribe()
    except Exception as e:
        print(f"Fehler bei der Spracherkennung: {e}")