"""
voXtext command line.

Examples:
    python cli.py lecture.mp4                          # transcribe, auto-detect language
    python cli.py lecture.mp4 --source ko --target en  # Korean video -> English subtitles
    python cli.py D:/Videos --target es --skip-existing
    python cli.py --list-languages
"""

import argparse
import sys
import time
from pathlib import Path

from core import __version__
from core import languages as L
from core.engine import Engine
from core.subtitles import FORMATS
from core.transcriber import WHISPER_MODELS, find_media
from core.translator import DEFAULT_NLLB, NLLB_MODELS


def list_languages():
    print(f"{'code':<7} {'language':<24} transcribe  translate")
    rows = [(c, n, True, bool(nl)) for c, (n, nl) in L.LANGUAGES.items()]
    rows += [(c, n, False, True) for c, (n, _) in L.EXTRA_TARGETS.items()]
    for code, name, tr, tl in sorted(rows, key=lambda r: r[1]):
        print(f"{code:<7} {name:<24} {'yes' if tr else '-':<11} {'yes' if tl else '-'}")


def main():
    ap = argparse.ArgumentParser(
        prog="cli.py",
        description="Offline video transcription and translation (Whisper + NLLB-200).")
    ap.add_argument("inputs", nargs="*", help="Video/audio files or folders")
    ap.add_argument("-s", "--source", default="auto",
                    help="Spoken language code or name, e.g. ko, Korean (default: auto)")
    ap.add_argument("-t", "--target", default="none",
                    help="Translate into this language, e.g. en, Spanish (default: none)")
    ap.add_argument("-f", "--formats", default="txt,srt,bilingual",
                    help=f"Comma list from: {','.join(FORMATS)}")
    ap.add_argument("-o", "--out", default=None, help="Output folder (default: next to each video)")
    ap.add_argument("--model", default="large-v3", choices=WHISPER_MODELS, help="Whisper model")
    ap.add_argument("--nllb", default=DEFAULT_NLLB, choices=list(NLLB_MODELS),
                    help="Translation model")
    ap.add_argument("--device", default="auto", choices=["auto", "cuda", "cpu"])
    ap.add_argument("--prompt", default=None, help="Names or terms that appear in the video")
    ap.add_argument("--beam-size", type=int, default=5)
    ap.add_argument("--no-vad", action="store_true", help="Don't skip silent parts")
    ap.add_argument("--skip-existing", action="store_true",
                    help="Skip videos that already have subtitles in the output folder")
    ap.add_argument("--list-languages", action="store_true", help="Show supported languages")
    ap.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = ap.parse_args()

    if args.list_languages:
        list_languages()
        return
    if not args.inputs:
        ap.error("give at least one video file or folder (or use --list-languages)")

    source, target = L.resolve(args.source), L.resolve(args.target)
    if source is None:
        sys.exit(f"Unknown source language '{args.source}'. See --list-languages.")
    if target is None or (target != L.NONE and not L.nllb_code(target)):
        sys.exit(f"Can't translate into '{args.target}'. See --list-languages.")
    formats = [f.strip() for f in args.formats.split(",") if f.strip()]
    bad = [f for f in formats if f not in FORMATS]
    if bad:
        sys.exit(f"Unknown format(s): {bad}. Choose from {FORMATS}")

    files = find_media(args.inputs)
    if not files:
        sys.exit("No video/audio files found.")
    print(f"Found {len(files)} file(s).  {L.name(source) if source != 'auto' else 'Auto-detect'}"
          + (f" → {L.name(target)}" if target != L.NONE else ""))

    from tqdm import tqdm
    engine = Engine(args.model, args.nllb, args.device,
                    on_warning=lambda m: print(f"\n[warning] {m}"))
    failures = 0
    for i, f in enumerate(files, 1):
        out_dir = Path(args.out) if args.out else f.parent
        if args.skip_existing and list(out_dir.glob(f"{f.stem}.*.srt")):
            print(f"[{i}/{len(files)}] skip (subtitles exist): {f.name}")
            continue
        print(f"\n[{i}/{len(files)}] {f.name}")
        bar = tqdm(total=100, bar_format="{l_bar}{bar}| {postfix}")

        def cb(frac, msg):
            bar.n = int(frac * 100)
            bar.set_postfix_str(msg)
            bar.refresh()

        try:
            r = engine.process(f, out_dir, source, target, formats, prompt=args.prompt,
                               beam_size=args.beam_size, vad=not args.no_vad, progress_cb=cb)
            bar.close()
            print(f"  {r['summary']}")
            for n in r["notes"]:
                print(f"  note: {n}")
            for p in r["files"]:
                print(f"  -> {p}")
        except Exception as e:
            bar.close()
            failures += 1
            print(f"  [error] {e}")
            time.sleep(0.1)
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
