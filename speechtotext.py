import queue
import time
from google.cloud import speech_v1p1beta1 as speech
import sounddevice as sd
from voice_commands import check_commands
from gptcalls import ask_chat_gpt
from texttospeech import speak
import numpy as np
import pvporcupine
import random
from config import hot_key, hotword_path0, hotword_path1, hotword_path2, hotword_params_path
import os


class SpeechRecognition():

    def __init__(self):
        try:
            self.credentials = os.environ['GOOGLE_APPLICATION_CREDENTIALS'] \
                                      = '/Users/VW7SYSB/Documents/Projects/JARVIS/JARenv/Google Credentials/credentialz.json'
            self.listening_phrases = ["Was kann ich für dich tun?",
                                      "Wie kann ich dir helfen?",
                                      "Wie kann ich dir behilflich sein?"]
            self.audio_queue = None
            self.client = None
            self.listening = False
            self.stream = None
            self.text = None
            self.recognition_active = True
            self.old_text = None
            self.setup_environment()
            self.processing = False
            self.counter = 0
        except Exception as e:
            print(f"Fehler bei der Initialisierung der JARVIS Startumgebung: {e}")

    def setup_environment(self):
        try:
            self.client = speech.SpeechClient()
            self.audio_queue = queue.Queue()

            # Wrapper function for the callback
            def wrapped_callback(indata, frames, time, status):
                self.callback(indata, frames, time, status)

            self.stream = sd.InputStream(
                samplerate=16000, channels=1, dtype='int16', blocksize=2048, callback=wrapped_callback)
            self.stream.start()
            print("JARVIS erfolgreich eingerichtet.")
        except Exception as e:
            print(f"Fehler bei der Einrichtung von JARVIS: {e}")

    def generator(self):
        while not self.audio_queue.empty() or self.listening:
            try:
                data = self.audio_queue.get(block=False)
            except queue.Empty:
                continue
            yield speech.StreamingRecognizeRequest(audio_content=data)

    def callback(self, indata, frames, time, status):
        if status:
            print(status)
        if self.listening:
            self.audio_queue.put_nowait(indata.tobytes())

    def hotword_detected(self):
        try:
            porcupine = pvporcupine.create(access_key=hot_key, keyword_paths=[
                                           hotword_path0, hotword_path1, hotword_path2], model_path=hotword_params_path)
            hotword_found = False
            buffer = np.zeros((porcupine.frame_length,), dtype=np.int16)

            def callback(indata, frames, time, status):
                nonlocal buffer
                nonlocal hotword_found
                if status:
                    print(status)
                if not hotword_found:
                    buffer[:] = indata[:, 0]
                    keyword_index = porcupine.process(buffer)
                    if keyword_index >= 0:
                        hotword_found = True
            with sd.InputStream(samplerate=porcupine.sample_rate, channels=1, dtype='int16', blocksize=porcupine.frame_length, callback=callback):
                while not hotword_found:
                    time.sleep(0.1)
            porcupine.delete()
            return hotword_found
        except Exception as e:
            print(f"Fehler bei der Erkennung des Aktivierungswortes: {e}")
            return False

    def handle_response(self, response):
        if self.counter == 1:
            self.counter = 0
            return None
        if self.processing:
            return None
        if response.results and response.results[0].is_final:
            self.text = response.results[0].alternatives[0].transcript
            self.processing = True
            print("Du hast gesagt: " + self.text)
            self.old_text = self.text
            self.recognition_active = True

            self.listening = False
            if check_commands(self.text):
                
                self.listening = False
                self.processing = False
                return None
            self.listening = True

            try:
                gpt_prompt = ask_chat_gpt(self.text)
                self.processing = False
                return gpt_prompt
            except Exception as e:
                print(f"Fehler bei der ChatGPT-Antwortgenerierung: {e}")
                gpt_prompt = "Entschuldigung, ich habe gerade Probleme bei der Generierung einer Antwort."
                return gpt_prompt

        return None

    def listen_and_transcribe(self):
        while True:
            try:
                if self.hotword_detected():
                    speak(random.choice(self.listening_phrases))
                    self.listening = True
                    if self.recognition_active:
                        requests = self.generator()
                        config = speech.RecognitionConfig(
                            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                            sample_rate_hertz=16000,
                            language_code='de-DE',
                            diarization_config=speech.SpeakerDiarizationConfig(
                                enable_speaker_diarization=True,
                                min_speaker_count=1,
                                max_speaker_count=3
                            )
                        )
                        streaming_config = speech.StreamingRecognitionConfig(
                            config=config)

                        responses = self.client.streaming_recognize(
                            streaming_config, requests)
                        self.recognition_active = False
                        if self.counter == 0:
                            for response in responses:
                                gpt_response = self.handle_response(response)
                                self.counter += 1
                                responses = None
                                if gpt_response:
                                    if response.results and response.results[0].is_final:
                                        self.listening = False
                                        try:
                                            speak(gpt_response)
                                        except Exception as e:
                                            print(
                                                f"Fehler bei der Text-zu-Sprache-Konvertierung: {e}")
                                        finally:
                                            print(
                                                "JARVIS bereit...")
                                            break
                            self.counter = 0
            except Exception as e:
                print(
                    f"Fehler beim Audio-Streaming oder bei der Spracherkennung: {e}")