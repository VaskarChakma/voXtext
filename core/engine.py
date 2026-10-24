"""High-level pipeline shared by the web app and the command line:
video -> transcript (Whisper) -> translation (NLLB) -> subtitle files."""

import time
from pathlib import Path

from . import languages as L
from .compat import GPU_FALLBACK_MSG, is_gpu_error
from .subtitles import fmt_short, write_outputs
from .transcriber import load_whisper, transcribe
from .translator import DEFAULT_NLLB, Translator


class Engine:
    """Keeps models loaded between files and falls back to CPU if the GPU fails."""

    def __init__(self, whisper_model="large-v3", nllb_model=DEFAULT_NLLB, device="auto",
                 on_warning=print):
        self.whisper_model = whisper_model
        self.nllb_model = nllb_model
        self.device = device
        self.on_warning = on_warning
        self._whisper = None
        self._translator = None

    def configure(self, whisper_model=None, nllb_model=None, device=None):
        """Change settings; reloads only the models that changed."""
        if device and device != self.device:
            self.device, self._whisper, self._translator = device, None, None
        if whisper_model and whisper_model != self.whisper_model:
            self.whisper_model, self._whisper = whisper_model, None
        if nllb_model and nllb_model != self.nllb_model:
            self.nllb_model, self._translator = nllb_model, None

    # -- model access ------------------------------------------------------
    def whisper(self):
        if self._whisper is None:
            self._whisper = load_whisper(self.whisper_model, self.device)
        return self._whisper

    def translator(self):
        if self._translator is None:
            self._translator = Translator(self.nllb_model, self.device)
        return self._translator

    def _gpu_fallback(self):
        self.on_warning(GPU_FALLBACK_MSG)
        self.device, self._whisper, self._translator = "cpu", None, None

    def _with_fallback(self, fn):
        try:
            return fn()
        except Exception as e:
            if self.device == "cpu" or not is_gpu_error(e):
                raise
            self._gpu_fallback()
            return fn()

    # -- pipeline ----------------------------------------------------------
    def process(self, path, out_dir=None, source="auto", target=None,
                formats=("txt", "srt"), prompt=None, beam_size=5, vad=True,
                progress_cb=None):
        """Transcribe (and optionally translate) one file.

        source: Whisper code ('ko') or 'auto'.  target: code ('en'), or None/'none'.
        Returns a dict with segments, detected language, written files and notes.
        """
        path = Path(path)
        out_dir = Path(out_dir) if out_dir else path.parent
        out_dir.mkdir(parents=True, exist_ok=True)
        target = None if target in (None, "", L.NONE) else target
        source = None if source in (None, "", L.AUTO) else source
        progress_cb = progress_cb or (lambda frac, msg: None)
        split = 0.85 if target else 1.0
        notes = []
        t0 = time.time()

        segments, detected, duration = self._with_fallback(lambda: transcribe(
            self.whisper(), path, language=source, beam_size=beam_size, vad=vad,
            initial_prompt=prompt,
            progress_cb=lambda f, m: progress_cb(f * split, f"Transcribing {m}")))
        src = source or detected

        if target:
            src_nllb, tgt_nllb = L.nllb_code(src), L.nllb_code(target)
            if src == target or src_nllb == tgt_nllb:
                notes.append(f"Video is already in {L.name(target)}, so no translation needed.")
                target = None
            elif not src_nllb:
                notes.append(f"Translation from {L.name(src)} isn't supported; "
                             "saved the original transcript only.")
                target = None
            elif segments:
                texts = [s["text"] for s in segments]
                translated = self._with_fallback(lambda: self.translator().translate(
                    texts, src_nllb, tgt_nllb,
                    progress_cb=lambda f, m: progress_cb(split + f * (1 - split),
                                                         f"Translating {m}")))
                for seg, tr in zip(segments, translated):
                    seg["translation"] = tr

        files = write_outputs(segments, out_dir / path.stem, formats, src, target)
        progress_cb(1.0, "Done")
        return {
            "segments": segments,
            "source": src,
            "target": target,
            "duration": duration,
            "elapsed": time.time() - t0,
            "files": files,
            "notes": notes,
            "summary": (f"{path.name}: {L.name(src)}"
                        + (f" → {L.name(target)}" if target else "")
                        + f", {len(segments)} lines, {fmt_short(duration)} of audio "
                          f"in {fmt_short(time.time() - t0)}"),
        }
