"""Text translation with Meta's NLLB-200, run through CTranslate2 for speed.

NLLB covers 200 languages and translates directly between any pair
(Korean -> Spanish, Japanese -> Arabic, ...), with no detour through English.
"""

from pathlib import Path

from .compat import pick_device
from .transcriber import MODELS_DIR

NLLB_MODELS = {
    "nllb-1.3b": "facebook/nllb-200-distilled-1.3B",
    "nllb-600m": "facebook/nllb-200-distilled-600M",
    "nllb-3.3b": "facebook/nllb-200-3.3B",
}
DEFAULT_NLLB = "nllb-1.3b"


def nllb_dir(key: str) -> Path:
    return MODELS_DIR / f"{key}-ct2"


def is_installed(key: str) -> bool:
    return (nllb_dir(key) / "model.bin").exists()


def convert_nllb(key: str = DEFAULT_NLLB, source=None):
    """Download an NLLB model from Hugging Face and convert it to CTranslate2 format.
    Needs internet and the 'transformers' + 'torch' packages, once.
    `source` can point to a local Hugging Face model folder instead."""
    from ctranslate2.converters import TransformersConverter
    from transformers import AutoTokenizer

    hf_name = source or NLLB_MODELS[key]
    out = nllb_dir(key)
    out.parent.mkdir(parents=True, exist_ok=True)
    print(f"Converting {hf_name} -> {out}  (one time only, this can take a while)...")
    TransformersConverter(hf_name, load_as_float16=True).convert(
        str(out), quantization="float16", force=True)
    AutoTokenizer.from_pretrained(hf_name).save_pretrained(str(out))
    print(f"Translation model ready: {out}")
    return out


class Translator:
    def __init__(self, key: str = DEFAULT_NLLB, device: str = "auto", model_path=None):
        import ctranslate2
        from transformers import AutoTokenizer

        path = Path(model_path) if model_path else nllb_dir(key)
        if not (path / "model.bin").exists():
            raise FileNotFoundError(
                f"Translation model '{key}' isn't installed. "
                f"Run once with internet:  python download_models.py --nllb {key}")
        self.device = pick_device(device)
        compute_type = "int8_float16" if self.device == "cuda" else "int8"
        self.model = ctranslate2.Translator(str(path), device=self.device,
                                            compute_type=compute_type)
        self.tokenizer = AutoTokenizer.from_pretrained(str(path))
        print(f"Loaded translator '{key}' on {self.device} ({compute_type}).")

    def translate(self, texts, src_nllb: str, tgt_nllb: str, batch_size: int = 16,
                  beam_size: int = 4, progress_cb=None):
        """Translate a list of strings. Language codes are NLLB/FLORES-200 codes."""
        tok = self.tokenizer
        tok.src_lang = src_nllb
        sources = [tok.convert_ids_to_tokens(tok.encode(t)) for t in texts]
        results = []
        for start in range(0, len(sources), batch_size):
            batch = sources[start:start + batch_size]
            out = self.model.translate_batch(
                batch,
                target_prefix=[[tgt_nllb]] * len(batch),
                beam_size=beam_size,
                max_decoding_length=256,
                repetition_penalty=1.1,
            )
            for r in out:
                hyp = r.hypotheses[0]
                if hyp and hyp[0] == tgt_nllb:
                    hyp = hyp[1:]
                results.append(tok.decode(tok.convert_tokens_to_ids(hyp),
                                          skip_special_tokens=True).strip())
            if progress_cb:
                done = min(start + batch_size, len(sources))
                progress_cb(done / len(sources), f"{done}/{len(sources)} lines")
        return results
