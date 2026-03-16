import numpy as np
import pyaudiowpatch as pyaudio
from google.cloud import speech_v1 as speech

SERVICE_ACCOUNT_FILE = r"D:\in_01\red-provider-449110-m8-d16a221f8413.json"
TARGET_RATE = 16000


def stream_transcripts():
    client = speech.SpeechClient.from_service_account_file(SERVICE_ACCOUNT_FILE)
    p = pyaudio.PyAudio()

    # Get default loopback device
    loopback = p.get_default_wasapi_loopback()
    input_rate = int(loopback["defaultSampleRate"])
    channels = 2
    chunk = int(input_rate / 10)

    stream = p.open(
        format=pyaudio.paInt16,
        channels=channels,
        rate=input_rate,
        input=True,
        input_device_index=loopback["index"],
        frames_per_buffer=chunk,
    )

    def convert_audio(data):
        audio = np.frombuffer(data, dtype=np.int16)

        # stereo -> mono
        audio = audio.reshape(-1, channels)
        audio = audio.mean(axis=1)

        # resample input_rate -> 16k
        duration = len(audio) / input_rate
        new_length = int(duration * TARGET_RATE)

        old_idx = np.linspace(0, 1, len(audio))
        new_idx = np.linspace(0, 1, new_length)

        resampled = np.interp(new_idx, old_idx, audio)
        return resampled.astype(np.int16).tobytes()

    def generator():
        while True:
            data = stream.read(chunk, exception_on_overflow=False)
            yield speech.StreamingRecognizeRequest(
                audio_content=convert_audio(data)
            )

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=TARGET_RATE,
        language_code="en-US",
        enable_automatic_punctuation=True,
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=False,
    )

    responses = client.streaming_recognize(streaming_config, generator())

    try:
        for response in responses:
            for result in response.results:
                if result.is_final:
                    transcript = result.alternatives[0].transcript.strip()
                    if transcript:
                        yield transcript
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()