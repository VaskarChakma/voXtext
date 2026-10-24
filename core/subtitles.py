"""Writers for transcript and subtitle files."""

from pathlib import Path

FORMATS = ["txt", "timestamps", "srt", "vtt", "bilingual"]
FORMAT_HELP = {
    "txt": "Plain text, one line per sentence",
    "timestamps": "Plain text with [hh:mm:ss] markers",
    "srt": "SubRip subtitles (most video players)",
    "vtt": "WebVTT subtitles (web players)",
    "bilingual": "SRT showing original + translation together",
}


def fmt_ts(seconds: float, sep: str = ",") -> str:
    ms = int(round(max(seconds, 0) * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02}{sep}{ms:03}"


def fmt_short(seconds: float) -> str:
    s = int(seconds)
    return f"{s // 3600:02}:{s % 3600 // 60:02}:{s % 60:02}"


def _write(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def render_txt(segments, key="text"):
    return "\n".join(s[key] for s in segments) + "\n"


def render_timestamps(segments, key="text"):
    return "\n".join(f"[{fmt_short(s['start'])}] {s[key]}" for s in segments) + "\n"


def render_srt(segments, key="text"):
    return "\n".join(
        f"{i}\n{fmt_ts(s['start'])} --> {fmt_ts(s['end'])}\n{s[key]}\n"
        for i, s in enumerate(segments, 1)
    )


def render_vtt(segments, key="text"):
    body = "\n".join(
        f"{fmt_ts(s['start'], '.')} --> {fmt_ts(s['end'], '.')}\n{s[key]}\n"
        for s in segments
    )
    return "WEBVTT\n\n" + body


def render_bilingual(segments):
    return "\n".join(
        f"{i}\n{fmt_ts(s['start'])} --> {fmt_ts(s['end'])}\n{s['text']}\n{s['translation']}\n"
        for i, s in enumerate(segments, 1)
    )


_RENDERERS = {
    "txt": (".txt", render_txt),
    "timestamps": ("_timestamps.txt", render_timestamps),
    "srt": (".srt", render_srt),
    "vtt": (".vtt", render_vtt),
}


def write_outputs(segments, base: Path, formats, source_lang: str, target_lang: str = None):
    """Write every requested format.

    Files are named like players expect, e.g. lecture.ko.srt and lecture.en.srt,
    so VLC and others can pick up subtitles automatically.
    """
    base = Path(base)
    written = []
    translated = bool(target_lang) and all("translation" in s for s in segments)

    for fmt in formats:
        if fmt == "bilingual":
            continue
        suffix, render = _RENDERERS[fmt]
        written.append(_write(base.with_name(f"{base.name}.{source_lang}{suffix}"),
                              render(segments, "text")))
        if translated:
            written.append(_write(base.with_name(f"{base.name}.{target_lang}{suffix}"),
                                  render(segments, "translation")))

    if "bilingual" in formats and translated:
        written.append(_write(
            base.with_name(f"{base.name}.{source_lang}-{target_lang}.srt"),
            render_bilingual(segments)))
    return written
