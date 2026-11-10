# import os
# import shutil
# import imageio_ffmpeg
# from dotenv import load_dotenv

# # 1. Environment variables (.env) load karein
# load_dotenv()

# # 2. FFmpeg setup: imageio-ffmpeg ke path ko process environment mein inject karein
# ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
# ffmpeg_dir = os.path.dirname(ffmpeg_exe)
# target_ffmpeg = os.path.join(ffmpeg_dir, "ffmpeg.exe")

# if not os.path.exists(target_ffmpeg):
#     shutil.copyfile(ffmpeg_exe, target_ffmpeg)

# os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")

# # 3. Project modules import karein
# from utils.audio_processor import process_input
# from core.transcriber import transcribe_all

# source = "https://youtu.be/oOFhb6z06Ho?si=_fiJRgO4sQhosS69"
# language = "hinglish"  # 'hinglish' ke liye Sarvam AI use hoga, 'english' ke liye local Whisper

# if __name__ == "__main__":
#     # Pre-check: Agar Sarvam use kar rahe hain to key verify kar lein
#     if language.lower() == "hinglish" and not os.getenv("SARVAM_API_KEY"):
#         raise ValueError(
#             "SARVAM_API_KEY environment variable set nahi hai! "
#             ".env file mein add karein: SARVAM_API_KEY=your_key_here"
#         )

#     print(f"Processing source: {source}")
#     chunks = process_input(source)
    
#     print(f"Audio chunks created: {len(chunks)}")
#     transcript = transcribe_all(chunks, language=language)
    
#     print("\n=== TRANSCRIPT ===\n")
#     print(transcript)

from dotenv import load_dotenv
load_dotenv()   # MUST be before any core/ imports

from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions


source = "https://www.youtube.com/watch?v=_Q-e_nczWqM&t=223s"
language = "english"   # "english" → Whisper, "hinglish" → Sarvam



chunks = process_input(source)


transcript = transcribe_all(chunks, language=language)
print("\n" + "=" * 60)
print("📝 TRANSCRIPT")
print("=" * 60)
print(transcript[:500] + "..." if len(transcript) > 500 else transcript)


title = generate_title(transcript)
summary = summarize(transcript)

print("\n" + "=" * 60)
print(f"📌 TITLE: {title}")
print("=" * 60)
print("\n📋 SUMMARY")
print("-" * 60)
print(summary)



action_items = extract_action_items(transcript)
decisions = extract_key_decisions(transcript)
questions = extract_questions(transcript)

print("\n" + "=" * 60)
print("✅ ACTION ITEMS")
print("=" * 60)
print(action_items)

print("\n" + "=" * 60)
print("🔑 KEY DECISIONS")
print("=" * 60)
print(decisions)

print("\n" + "=" * 60)
print("❓ OPEN QUESTIONS")
print("=" * 60)
print(questions)