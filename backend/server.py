import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from stt_loopback import stream_transcripts

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/transcript/stream")
def transcript_stream():
    def event_generator():
        print("App Started for transcript...")
        try:
            for transcript in stream_transcripts():
                payload = json.dumps({"transcript": transcript})
                yield f"data: {payload}\n\n"
        except Exception as e:
            payload = json.dumps({"error": str(e)})
            yield f"data: {payload}\n\n"

    return StreamingResponse(   
        event_generator(),
        media_type="text/event-stream"
    )