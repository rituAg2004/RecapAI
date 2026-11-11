# 🎬 RecapAI - AI Video Assistant

A free AI Meeting Assistant built in Python. Give it a YouTube URL or an audio/video file, and it transcribes, summarizes, extracts action items and decisions, and lets you chat with your meeting using RAG.

## ✨ Features

- YouTube URL or local audio/video file as input
- English transcription with local Whisper
- Hindi & Hinglish transcription with Sarvam AI
- Summary, action items (owner + deadline), key decisions, open questions
- Chat with your meeting using RAG + ChromaDB
- Streamlit UI and CLI

## 🛠️ Tech Stack

Python • OpenAI Whisper • Sarvam AI • LangChain (LCEL) • Mistral AI • ChromaDB • HuggingFace Embeddings • Streamlit

## 📂 Project Structure

```
AI-Video-Assistant/
├── app.py                  # Streamlit UI
├── main.py                 # CLI
├── requirements.txt
├── .env
├── core/
│   ├── transcriber.py
│   ├── translator.py
│   ├── summarizer.py
│   ├── extractor.py
│   ├── vector_store.py
│   └── rag_engine.py
└── utils/
    └── audio_processor.py
```

## 🚀 Setup

```bash
git clone https://github.com/rituAg2004/RecapAI.git
cd AI-Video-Assistant-

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
```

FFmpeg must be installed on your system.

Get free API keys from [Mistral](https://console.mistral.ai) and [Sarvam](https://dashboard.sarvam.ai), then create a `.env` file:

```env
MISTRAL_API_KEY=your_mistral_api_key
SARVAM_API_KEY=your_sarvam_api_key
```

## ▶️ Usage

**Streamlit UI**

```bash
streamlit run app.py
```

**CLI**

```bash
python main.py
```
