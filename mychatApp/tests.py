# from django.test import TestCase
from openai import OpenAI
import sounddevice as sd
import wavio

OPENAI_API_KEY = "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"
client = OpenAI(api_key=OPENAI_API_KEY)

def record_audio(duration=5, fs=44100):
    print("Recording...")
    file = sd.rec(int(duration * fs), samplerate=fs, channels=2)
    sd.wait()  # Wait until recording is finished
    print("Finished recording.")
    wav_filename = "file.wav"
    wavio.write(wav_filename, file, fs, sampwidth=2)
    return wav_filename

def transcribe(wav_filename):
    audio_data = open(wav_filename, "rb")

    # Get the audio data from the request
    # Send the audio data to the Whisper ASR API
    transcript = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_data,
        response_format="text"
    )
    # Return the transcribed text
    return transcript

transcribed_text = transcribe(wav_filename=record_audio())
print(transcribed_text)

# Create your tests here.
