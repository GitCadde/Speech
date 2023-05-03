import tempfile
import os
from google.cloud import texttospeech
import threading
import simpleaudio as sa

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/VW7SYSB/Downloads/credentialz.json'

pa_lock = threading.Lock()


def play_audio(fp):
    with pa_lock:
        wave_obj = sa.WaveObject.from_wave_file(fp)
        play_obj = wave_obj.play()
        play_obj.wait_done()


def speak(text):
    client = texttospeech.TextToSpeechClient()
    input_text = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code='de-DE', name='de-DE-Neural2-B')
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16,
        speaking_rate=1.1)

    response = client.synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config)

    with tempfile.NamedTemporaryFile(delete=True) as fp:
        fp.write(response.audio_content)
        fp.seek(0)

        play_thread = threading.Thread(target=play_audio, args=(fp.name,))
        play_thread.start()
        play_thread.join()