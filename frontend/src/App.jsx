import { useEffect, useRef, useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export default function App() {
  const [allText, setAllText] = useState("");
  const [isListening, setIsListening] = useState(false);
  const [status, setStatus] = useState("Idle");
  const eventSourceRef = useRef(null);
  const textareaRef = useRef(null);

  const startListening = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    setStatus("Connecting...");
    setIsListening(true);

    const es = new EventSource(`${API_BASE}/api/transcript/stream`);
    eventSourceRef.current = es;

    es.onopen = () => {
      setStatus("Listening...");
    };

    es.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.error) {
          setStatus(`Error: ${data.error}`);
          setIsListening(false);
          es.close();
          return;
        }

        if (data.transcript) {
          setAllText((prev) => prev + data.transcript + "\n");
        }
      } catch (err) {
        console.error("SSE parse error:", err, event.data);
        setStatus("Invalid stream message");
      }
    };

    es.onerror = () => {
      setStatus("Stream disconnected");
      setIsListening(false);
      es.close();
    };
  };

  const stopListening = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setIsListening(false);
    setStatus("Stopped");
  };

  const clearText = () => {
    setAllText("");
  };

  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.scrollTop = textareaRef.current.scrollHeight;
    }
  }, [allText]);

  return (
    <div style={{ maxWidth: 900, margin: "40px auto", fontFamily: "Arial" }}>
      <h1>Live Transcript Demo</h1>

      <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
        <button onClick={startListening} disabled={isListening}>
          Start
        </button>

        <button onClick={stopListening} disabled={!isListening}>
          Stop
        </button>

        <button onClick={clearText}>
          Clear
        </button>
      </div>

      <p><b>Status:</b> {status}</p>

      <textarea
        ref={textareaRef}
        value={allText}
        readOnly
        rows={16}
        style={{
          width: "100%",
          padding: 12,
          borderRadius: 8,
          border: "1px solid #ccc",
          resize: "vertical"
        }}
      />
    </div>
  );
}