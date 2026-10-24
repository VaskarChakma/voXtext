"""Speech-to-text with faster-whisper (an optimised Whisper implementation)."""

from pathlib import Path

from .compat import pick_device

PROJECT_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = PROJECT_DIR / "models"

WHISPER_MODELS = ["large-v3", "large-v3-turbo", "medium", "small", "base", "tiny"]

MEDIA_EXTS = {
    ".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv", ".wmv", ".m4v", ".ts", ".mts",
    ".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".opus", ".wma",
}


def find_media(inputs):
    """Expand files and folders into a list of media files."""
    files = []
    for item in inputs:
        p = Path(str(item).strip().strip('"')).expanduser()
        if p.is_dir():
            files += sorted(f for f in p.rglob("*") if f.suffix.lower() in MEDIA_EXTS)
        elif p.is_file():
            files.append(p)
        else:
            print(f"[skip] Not found: {p}")
    return files


def load_whisper(name="large-v3", device="auto", compute_type="auto"):
    """Load from ./models; download only if it isn't there yet."""
    from faster_whisper import WhisperModel

    device = pick_device(device)
    if compute_type == "auto":
        compute_type = "float16" if device == "cuda" else "int8"
    MODELS_DIR.mkdir(exist_ok=True)
    kwargs = dict(device=device, compute_type=compute_type, download_root=str(MODELS_DIR))
    try:
        model = WhisperModel(name, local_files_only=True, **kwargs)
    except Exception:
        print(f"Whisper model '{name}' not found locally. Downloading once (needs internet)...")
        model = WhisperModel(name, **kwargs)
    print(f"Loaded Whisper '{name}' on {device} ({compute_type}).")
    return model


def transcribe(model, path, language=None, beam_size=5, vad=True, initial_prompt=None,
               progress_cb=None):
    """Return (segments, detected_language, duration).
    progress_cb(fraction, message) is called as audio is processed."""
    from .subtitles import fmt_short

    seg_iter, info = model.transcribe(
        str(path),
        language=language or None,
        beam_size=beam_size,
        vad_filter=vad,
        vad_parameters=dict(min_silence_duration_ms=500),
        initial_prompt=initial_prompt or None,
        condition_on_previous_text=False,  # avoids repeated-line loops on long videos
    )
    duration = info.duration or 0
    segments = []
    for seg in seg_iter:
        text = seg.text.strip()
        if text:
            segments.append({"start": seg.start, "end": seg.end, "text": text})
        if progress_cb and duration:
            progress_cb(min(seg.end / duration, 1.0),
                        f"{fmt_short(seg.end)} / {fmt_short(duration)}")
    return segments, info.language, duration
