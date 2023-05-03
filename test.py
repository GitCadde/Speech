import tempfile
import requests
from bs4 import BeautifulSoup
import youtube_dl
from moviepy.editor import *
from pydub import AudioSegment
from pydub.playback import play


def play_news():
    # 1. URL des neuesten Videos abrufen
    url = 'https://www.tagesschau.de/100sekunden/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    video_url = 'https:' + soup.find('iframe')['src']

    # 2. Video herunterladen
    with tempfile.NamedTemporaryFile(suffix='.mp4') as video_tempfile:
        ydl_opts = {'format': 'bestaudio/best', 'outtmpl': video_tempfile.name}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        # 3. Audio aus dem Video extrahieren
        video = VideoFileClip(video_tempfile.name)
        audio = video.audio

        with tempfile.NamedTemporaryFile(suffix='.mp3') as audio_tempfile:
            audio.write_audiofile(audio_tempfile.name)

            # 4. Audio abspielen
            audio_file = AudioSegment.from_mp3(audio_tempfile.name)
            play(audio_file)

if __name__ == '__main__':
    play_news()