"""Core engine: offline transcription (faster-whisper) and translation (NLLB-200)."""

from . import compat  # noqa: F401  (must run before faster-whisper / ctranslate2 load)

__version__ = "1.0.0"
