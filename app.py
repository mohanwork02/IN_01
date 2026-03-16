import streamlit as st

st.set_page_config(page_title="Tab Sharing Demo", layout="wide")
st.title("Simple Tab Sharing Demo")

st.html("""
<div style="padding:20px;border:1px solid #ddd;border-radius:12px;">
    <h3>Share your browser tab / screen</h3>
    <p>Click <b>Start Sharing</b>, then choose the tab/window/screen you want to share.</p>

    <button id="startBtn" style="padding:10px 18px;margin-right:10px;border:none;border-radius:8px;cursor:pointer;">
        Start Sharing
    </button>

    <button id="stopBtn" style="padding:10px 18px;border:none;border-radius:8px;cursor:pointer;">
        Stop Sharing
    </button>

    <p id="status" style="margin-top:12px;color:#444;">Status: Idle</p>

    <br>

    <video id="screenVideo" autoplay playsinline controls
           style="width:100%;max-width:900px;border:1px solid #ccc;border-radius:10px;background:black;">
    </video>
</div>

<script>
let stream = null;

async function startShare() {
    const status = document.getElementById("status");
    const video = document.getElementById("screenVideo");

    try {
        status.innerText = "Status: Requesting permission...";

        stream = await navigator.mediaDevices.getDisplayMedia({
            video: true,
            audio: true
        });

        video.srcObject = stream;
        status.innerText = "Status: Sharing started";

        const tracks = stream.getVideoTracks();
        if (tracks.length > 0) {
            tracks[0].addEventListener("ended", () => {
                stopShare();
            });
        }
    } catch (err) {
        status.innerText = "Status: Failed - " + err.name + " : " + err.message;
        console.error("Screen share error:", err);
    }
}

function stopShare() {
    const status = document.getElementById("status");
    const video = document.getElementById("screenVideo");

    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }

    video.srcObject = null;
    status.innerText = "Status: Sharing stopped";
}

document.getElementById("startBtn").addEventListener("click", startShare);
document.getElementById("stopBtn").addEventListener("click", stopShare);
</script>
""", unsafe_allow_javascript=True)