import os
import imageio_ffmpeg
from pydub import AudioSegment
import yt_dlp

# Point pydub to the ffmpeg executable bundled via imageio_ffmpeg
ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
AudioSegment.converter = ffmpeg_exe

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_youtube_audio(url: str) -> str:
    # Use video ID in output template to avoid filename escaping issues
    output_template = os.path.join(DOWNLOAD_DIR, "%(id)s.%(ext)s")

    ydl_opts = {
        "format": "ba/ba*",
        "outtmpl": output_template,
        "ffmpeg_location": ffmpeg_exe,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        # Bypass YouTube 403 Forbidden by routing through mobile clients
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "ios", "web"],
                "player_skip": ["webpage", "configs"],
            }
        },
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        },
        "quiet": False,
        "no_warnings": False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        # Construct the final expected .wav filepath based on video ID
        video_id = info.get("id")
        wav_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.wav")

        if not os.path.exists(wav_path):
            base_file = ydl.prepare_filename(info)
            wav_path = os.path.splitext(base_file)[0] + ".wav"

    return wav_path


def convert_to_wav(input_path: str) -> str:
    """Normalize any audio/video file to 16 kHz mono WAV for speech models."""
    base_name = os.path.splitext(input_path)[0]
    output_path = f"{base_name}_16k_mono.wav"

    # Avoid re-converting if it was already processed
    if input_path.endswith("_16k_mono.wav"):
        return input_path

    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export(output_path, format="wav")
    return output_path


def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list[str]:
    """Split WAV file into fixed-duration segments."""
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000
    chunks = []

    base_path = os.path.splitext(wav_path)[0]

    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start : start + chunk_ms]
        chunk_path = f"{base_path}_chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)

    return chunks


def process_input(source: str) -> list[str]:
    is_url = any(
        source.lower().startswith(prefix)
        for prefix in ("http://", "https://", "www.youtube.com", "youtu.be")
    )

    if is_url:
        print("Detected YouTube URL. Downloading audio...")
        raw_audio = download_youtube_audio(source)
    else:
        print("Detected local file...")
        raw_audio = source

    print("Normalizing audio format (16 kHz, Mono)...")
    normalized_wav = convert_to_wav(raw_audio)

    print("Chunking audio...")
    chunks = chunk_audio(normalized_wav)
    print(f"Audio ready - {len(chunks)} chunk(s) created.")
    return chunks


if __name__ == "__main__":
    test_url = "https://youtu.be/mtiOK2QG9Q0?si=WTXWLlAghbSAOvvV"
    chunk_files = process_input(test_url)
    print("Generated chunks:", chunk_files)