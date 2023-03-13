# Note: you need to be using OpenAI Python v0.27.0 for the code below to work
import openai


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


openai.api_key = open_file('openaikey.txt')

audio_file = open("Test.mp3", "rb")

transcript = openai.Audio.transcribe("whisper-1", audio_file)
print(transcript)
