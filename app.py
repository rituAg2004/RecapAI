import os
import tempfile

import streamlit as st
from dotenv import load_dotenv

from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import (
    extract_action_items,
    extract_key_decisions,
    extract_questions,
)
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()

st.set_page_config(
    page_title="AI Video Assistant",
    page_icon="🎬",
    layout="wide",
)

# ---------- Styling ----------
st.markdown(
    """
    <style>
    .block-container {padding-top: 2rem; max-width: 1100px;}
    .hero {
        padding: 1.4rem 1.6rem;
        border-radius: 16px;
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
        margin-bottom: 1.2rem;
    }
    .hero h1 {margin: 0; font-size: 2rem; color: white;}
    .hero p {margin: .3rem 0 0 0; opacity: .9;}
    .title-card {
        padding: 1rem 1.2rem;
        border-radius: 12px;
        border: 1px solid rgba(128,128,128,.25);
        margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>🎬 AI Video Assistant</h1>
        <p>Turn any YouTube video or recording into a transcript, summary,
        action items, decisions, and a chat you can ask questions.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- Session state ----------
if "result" not in st.session_state:
    st.session_state.result = None
if "messages" not in st.session_state:
    st.session_state.messages = []


# ---------- Pipeline ----------
def run_pipeline_ui(source: str, language: str) -> dict:
    """Same steps as the CLI pipeline, with live progress in the UI."""
    with st.status("Processing...", expanded=True) as status:
        st.write("📥 Downloading / splitting audio...")
        chunks = process_input(source)

        st.write("📝 Transcribing...")
        transcript = transcribe_all(chunks, language)

        st.write("🏷️ Generating title...")
        title = generate_title(transcript)

        st.write("📋 Summarizing...")
        summary = summarize(transcript)

        st.write("✅ Extracting action items...")
        action_items = extract_action_items(transcript)

        st.write("🔑 Extracting key decisions...")
        decisions = extract_key_decisions(transcript)

        st.write("❓ Extracting open questions...")
        questions = extract_questions(transcript)

        st.write("🧠 Building chat index...")
        rag_chain = build_rag_chain(transcript)

        status.update(label="Done!", state="complete", expanded=False)

    return {
        "title": title,
        "transcript": transcript,
        "summary": summary,
        "action_items": action_items,
        "key_decisions": decisions,
        "open_questions": questions,
        "rag_chain": rag_chain,
    }


def build_report(r: dict) -> str:
    return (
        f"# {r['title']}\n\n"
        f"## Summary\n{r['summary']}\n\n"
        f"## Action Items\n{r['action_items']}\n\n"
        f"## Key Decisions\n{r['key_decisions']}\n\n"
        f"## Open Questions\n{r['open_questions']}\n\n"
        f"## Transcript\n{r['transcript']}\n"
    )


# ---------- Sidebar ----------
with st.sidebar:
    st.header("⚙️ Input")
    input_type = st.radio("Source type", ["YouTube URL", "Upload file"])
    language = st.selectbox("Language", ["english", "hinglish"])

    source = None
    if input_type == "YouTube URL":
        source = st.text_input("YouTube URL", placeholder="https://youtube.com/watch?v=...")
    else:
        uploaded = st.file_uploader(
            "Audio / video file",
            type=["mp3", "wav", "m4a", "mp4", "mkv", "webm", "mov", "aac", "ogg"],
        )
        if uploaded is not None:
            suffix = os.path.splitext(uploaded.name)[1]
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            tmp.write(uploaded.getbuffer())
            tmp.close()
            source = tmp.name

    run_clicked = st.button("🚀 Analyze", type="primary", use_container_width=True)

    if st.session_state.result and st.button("🗑️ Clear results", use_container_width=True):
        st.session_state.result = None
        st.session_state.messages = []
        st.rerun()

# ---------- Run ----------
if run_clicked:
    if not source:
        st.warning("Please provide a YouTube URL or upload a file first.")
    else:
        try:
            st.session_state.result = run_pipeline_ui(source.strip(), language)
            st.session_state.messages = []
        except Exception as e:
            st.error(f"Something went wrong: {e}")

# ---------- Results ----------
result = st.session_state.result

if result is None:
    st.info("👈 Choose a source in the sidebar and click **Analyze** to get started.")
else:
    st.markdown(
        f'<div class="title-card"><b>📌 Title</b><br><span style="font-size:1.3rem">'
        f'{result["title"]}</span></div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Transcript words", f"{len(result['transcript'].split()):,}")
    col2.metric("Language", language.capitalize())
    col3.download_button(
        "⬇️ Download report (.md)",
        data=build_report(result),
        file_name="video_report.md",
        mime="text/markdown",
        use_container_width=True,
    )

    tab_summary, tab_actions, tab_decisions, tab_questions, tab_transcript, tab_chat = st.tabs(
        ["📋 Summary", "✅ Action Items", "🔑 Decisions", "❓ Questions", "📄 Transcript", "💬 Chat"]
    )

    with tab_summary:
        st.markdown(result["summary"])

    with tab_actions:
        st.markdown(result["action_items"])

    with tab_decisions:
        st.markdown(result["key_decisions"])

    with tab_questions:
        st.markdown(result["open_questions"])

    with tab_transcript:
        st.text_area("Full transcript", result["transcript"], height=450)
        st.download_button(
            "⬇️ Download transcript (.txt)",
            data=result["transcript"],
            file_name="transcript.txt",
            mime="text/plain",
        )

    with tab_chat:
        st.caption("Ask anything about the video. Answers come from the transcript.")

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if question := st.chat_input("Ask a question about the video..."):
            st.session_state.messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        answer = ask_question(result["rag_chain"], question)
                    except Exception as e:
                        answer = f"Sorry, I hit an error: {e}"
                st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})