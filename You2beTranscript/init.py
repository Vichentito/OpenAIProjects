import openai
import yt_dlp
from moviepy.editor import *
from pydub import AudioSegment


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


def download_audio_from_youtube(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'youtube_audio.%(ext)s',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return 'youtube_audio.mp3'


def split_audio_file(audio_path, segment_duration_ms):
    audio = AudioSegment.from_mp3(audio_path)
    segments = []

    for i in range(0, len(audio), segment_duration_ms):
        segment = audio[i:i + segment_duration_ms]
        segment_path = f"segment_{i // segment_duration_ms}.mp3"
        segment.export(segment_path, format="mp3")
        segments.append(segment_path)

    return segments


openai.api_key = open_file('openaikey.txt')

# Reemplaza esto con la URL del video de YouTube que deseas transcribir
youtube_url = "https://www.youtube.com/watch?v=UsT11sOD1JA"
audio_file_path = download_audio_from_youtube(youtube_url)

# Dividir el audio en segmentos de 10 minutos
segment_duration_ms = 10 * 60 * 1000
audio_segments = split_audio_file(audio_file_path, segment_duration_ms)

# Guardar la transcripción completa en un archivo de texto
with open("transcription.txt", "w", encoding="utf-8") as transcription_file:
    for segment_path in audio_segments:
        with open(segment_path, "rb") as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
            transcription_file.write(transcript.text)
            transcription_file.write("\n")

print("Transcripción guardada en transcription.txt")
