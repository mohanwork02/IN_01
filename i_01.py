import pyaudio
from google.cloud import speech_v1 as speech

client = speech.SpeechClient.from_service_account_file(
    r"D:\in_01\red-provider-449110-m8-d16a221f8413.json"
)

RATE = 16000
CHUNK = int(RATE / 10)

p = pyaudio.PyAudio()

stream = p.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK
)

def generator():
    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        yield speech.StreamingRecognizeRequest(audio_content=data)

config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=RATE,
    language_code="en-US",
)

streaming_config = speech.StreamingRecognitionConfig(
    config=config,
    interim_results=True,
)

responses = client.streaming_recognize(streaming_config, generator())

for response in responses:
    for result in response.results:
        transcript = result.alternatives[0].transcript
        if result.is_final:
            print("FINAL:", transcript)
        else:
            print("INTERIM:", transcript)