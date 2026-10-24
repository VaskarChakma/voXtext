"""
Download the models once (needs internet). Afterwards everything runs offline.

    python download_models.py                         # large-v3 + nllb-1.3b (defaults)
    python download_models.py --whisper large-v3-turbo
    python download_models.py --nllb nllb-600m
    python download_models.py --skip-translation      # speech-to-text only
"""

import argparse

import core  # noqa: F401  (applies compatibility fixes)
from core.transcriber import WHISPER_MODELS, load_whisper
from core.translator import DEFAULT_NLLB, NLLB_MODELS, convert_nllb, is_installed


def main():
    ap = argparse.ArgumentParser(description="Download models for offline use")
    ap.add_argument("--whisper", nargs="*", default=["large-v3"], choices=WHISPER_MODELS)
    ap.add_argument("--nllb", nargs="*", default=[DEFAULT_NLLB], choices=list(NLLB_MODELS))
    ap.add_argument("--skip-translation", action="store_true")
    ap.add_argument("--force", action="store_true", help="Re-convert translation models")
    args = ap.parse_args()

    for name in args.whisper:
        print(f"\n== Whisper {name} ==")
        load_whisper(name, device="cpu", compute_type="int8")

    if not args.skip_translation:
        for key in args.nllb:
            print(f"\n== Translation model {key} ==")
            if is_installed(key) and not args.force:
                print("Already installed.")
                continue
            convert_nllb(key)

    print("\nAll set. Models are in the 'models' folder; you can now work offline.")


if __name__ == "__main__":
    main()
