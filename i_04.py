import streamlit as st
import numpy as np
import pyaudiowpatch as pyaudio
from google.cloud import speech_v1 as speech

st.title("Live Transcript Demo")

if "all_text" not in st.session_state:
    st.session_state.all_text = ""

transcript_placeholder = st.empty()

# Initial empty box
transcript_placeholder.text_area(
    "Transcript",
    value=st.session_state.all_text,
    height=300,
    disabled=True,
    key="transcript_initial"
)

if st.button("Start"):
    st.session_state.all_text = ""

    # Google credentials
    client = speech.SpeechClient.from_service_account_file(
        r"D:\in_01\red-provider-449110-m8-d16a221f8413.json"
    )

    TARGET_RATE = 16000
    p = pyaudio.PyAudio()

    # Get default loopback device
    loopback = p.get_default_wasapi_loopback()
    INPUT_RATE = int(loopback["defaultSampleRate"])
    CHANNELS = 2
    CHUNK = int(INPUT_RATE / 10)

    st.write("Using device:", loopback["name"])
    st.write("Input rate:", INPUT_RATE)

    stream = p.open(
        format=pyaudio.paInt16,
        channels=CHANNELS,
        rate=INPUT_RATE,
        input=True,
        input_device_index=loopback["index"],
        frames_per_buffer=CHUNK,
    )

    # -----------------------------
    # Audio conversion
    # -----------------------------
    def convert_audio(data):
        audio = np.frombuffer(data, dtype=np.int16)

        # stereo -> mono
        audio = audio.reshape(-1, CHANNELS)
        audio = audio.mean(axis=1)

        # resample 48k -> 16k
        duration = len(audio) / INPUT_RATE
        new_length = int(duration * TARGET_RATE)

        old_idx = np.linspace(0, 1, len(audio))
        new_idx = np.linspace(0, 1, new_length)

        resampled = np.interp(new_idx, old_idx, audio)
        return resampled.astype(np.int16).tobytes()

    # -----------------------------
    # Generator
    # -----------------------------
    def generator():
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            yield speech.StreamingRecognizeRequest(
                audio_content=convert_audio(data)
            )

    # -----------------------------
    # Google STT config
    # -----------------------------
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=TARGET_RATE,
        language_code="en-US",
        enable_automatic_punctuation=True,
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=False
    )

    responses = client.streaming_recognize(streaming_config, generator())
    st.write("Listening to system audio...")

    try:
        for response in responses:
            for result in response.results:
                if result.is_final:
                    transcript = result.alternatives[0].transcript.strip()
                    if transcript:
                        # Instead of print(transcript), push it to frontend
                        st.session_state.all_text += transcript + "\n"

                        transcript_placeholder.text_area(
                            "Transcript",
                            value=st.session_state.all_text,
                            height=300,
                            disabled=True,
                            key=f"transcript_live_{len(st.session_state.all_text)}"
                        )
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()