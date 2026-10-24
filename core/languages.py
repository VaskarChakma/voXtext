"""Language tables.

Whisper (speech recognition) uses ISO-style codes such as "ko".
NLLB-200 (translation) uses FLORES-200 codes such as "kor_Hang".
"""

# whisper_code: (English name, NLLB code or None if NLLB can't translate it)
LANGUAGES = {
    "af": ("Afrikaans", "afr_Latn"),
    "sq": ("Albanian", "als_Latn"),
    "am": ("Amharic", "amh_Ethi"),
    "ar": ("Arabic", "arb_Arab"),
    "hy": ("Armenian", "hye_Armn"),
    "as": ("Assamese", "asm_Beng"),
    "az": ("Azerbaijani", "azj_Latn"),
    "ba": ("Bashkir", "bak_Cyrl"),
    "eu": ("Basque", "eus_Latn"),
    "be": ("Belarusian", "bel_Cyrl"),
    "bn": ("Bengali", "ben_Beng"),
    "bs": ("Bosnian", "bos_Latn"),
    "br": ("Breton", None),
    "bg": ("Bulgarian", "bul_Cyrl"),
    "my": ("Burmese", "mya_Mymr"),
    "yue": ("Cantonese", "yue_Hant"),
    "ca": ("Catalan", "cat_Latn"),
    "zh": ("Chinese", "zho_Hans"),
    "hr": ("Croatian", "hrv_Latn"),
    "cs": ("Czech", "ces_Latn"),
    "da": ("Danish", "dan_Latn"),
    "nl": ("Dutch", "nld_Latn"),
    "en": ("English", "eng_Latn"),
    "et": ("Estonian", "est_Latn"),
    "fo": ("Faroese", "fao_Latn"),
    "fi": ("Finnish", "fin_Latn"),
    "fr": ("French", "fra_Latn"),
    "gl": ("Galician", "glg_Latn"),
    "ka": ("Georgian", "kat_Geor"),
    "de": ("German", "deu_Latn"),
    "el": ("Greek", "ell_Grek"),
    "gu": ("Gujarati", "guj_Gujr"),
    "ht": ("Haitian Creole", "hat_Latn"),
    "ha": ("Hausa", "hau_Latn"),
    "haw": ("Hawaiian", None),
    "he": ("Hebrew", "heb_Hebr"),
    "hi": ("Hindi", "hin_Deva"),
    "hu": ("Hungarian", "hun_Latn"),
    "is": ("Icelandic", "isl_Latn"),
    "id": ("Indonesian", "ind_Latn"),
    "it": ("Italian", "ita_Latn"),
    "ja": ("Japanese", "jpn_Jpan"),
    "jw": ("Javanese", "jav_Latn"),
    "kn": ("Kannada", "kan_Knda"),
    "kk": ("Kazakh", "kaz_Cyrl"),
    "km": ("Khmer", "khm_Khmr"),
    "ko": ("Korean", "kor_Hang"),
    "lo": ("Lao", "lao_Laoo"),
    "la": ("Latin", None),
    "lv": ("Latvian", "lvs_Latn"),
    "ln": ("Lingala", "lin_Latn"),
    "lt": ("Lithuanian", "lit_Latn"),
    "lb": ("Luxembourgish", "ltz_Latn"),
    "mk": ("Macedonian", "mkd_Cyrl"),
    "mg": ("Malagasy", "plt_Latn"),
    "ms": ("Malay", "zsm_Latn"),
    "ml": ("Malayalam", "mal_Mlym"),
    "mt": ("Maltese", "mlt_Latn"),
    "mi": ("Maori", "mri_Latn"),
    "mr": ("Marathi", "mar_Deva"),
    "mn": ("Mongolian", "khk_Cyrl"),
    "ne": ("Nepali", "npi_Deva"),
    "no": ("Norwegian", "nob_Latn"),
    "nn": ("Norwegian Nynorsk", "nno_Latn"),
    "oc": ("Occitan", "oci_Latn"),
    "ps": ("Pashto", "pbt_Arab"),
    "fa": ("Persian", "pes_Arab"),
    "pl": ("Polish", "pol_Latn"),
    "pt": ("Portuguese", "por_Latn"),
    "pa": ("Punjabi", "pan_Guru"),
    "ro": ("Romanian", "ron_Latn"),
    "ru": ("Russian", "rus_Cyrl"),
    "sa": ("Sanskrit", "san_Deva"),
    "sr": ("Serbian", "srp_Cyrl"),
    "sn": ("Shona", "sna_Latn"),
    "sd": ("Sindhi", "snd_Arab"),
    "si": ("Sinhala", "sin_Sinh"),
    "sk": ("Slovak", "slk_Latn"),
    "sl": ("Slovenian", "slv_Latn"),
    "so": ("Somali", "som_Latn"),
    "es": ("Spanish", "spa_Latn"),
    "su": ("Sundanese", "sun_Latn"),
    "sw": ("Swahili", "swh_Latn"),
    "sv": ("Swedish", "swe_Latn"),
    "tl": ("Tagalog", "tgl_Latn"),
    "tg": ("Tajik", "tgk_Cyrl"),
    "ta": ("Tamil", "tam_Taml"),
    "tt": ("Tatar", "tat_Cyrl"),
    "te": ("Telugu", "tel_Telu"),
    "th": ("Thai", "tha_Thai"),
    "bo": ("Tibetan", "bod_Tibt"),
    "tr": ("Turkish", "tur_Latn"),
    "tk": ("Turkmen", "tuk_Latn"),
    "uk": ("Ukrainian", "ukr_Cyrl"),
    "ur": ("Urdu", "urd_Arab"),
    "uz": ("Uzbek", "uzn_Latn"),
    "vi": ("Vietnamese", "vie_Latn"),
    "cy": ("Welsh", "cym_Latn"),
    "yi": ("Yiddish", "ydd_Hebr"),
    "yo": ("Yoruba", "yor_Latn"),
}

# Translation-only targets (Whisper doesn't output these, but NLLB can write them).
EXTRA_TARGETS = {
    "zh-TW": ("Chinese (Traditional)", "zho_Hant"),
}

AUTO = "auto"
NONE = "none"


def name(code: str) -> str:
    if code in LANGUAGES:
        return LANGUAGES[code][0]
    if code in EXTRA_TARGETS:
        return EXTRA_TARGETS[code][0]
    return code


def nllb_code(code: str):
    if code in LANGUAGES:
        return LANGUAGES[code][1]
    if code in EXTRA_TARGETS:
        return EXTRA_TARGETS[code][1]
    return None


def resolve(value: str):
    """Accept a code ('ko'), an English name ('Korean') or a dropdown label
    ('Korean (ko)') and return the code. Returns None if unknown."""
    if not value:
        return None
    v = value.strip()
    if v.endswith(")") and "(" in v:
        v = v[v.rfind("(") + 1:-1]
    low = v.lower()
    if low in (AUTO, NONE):
        return low
    for table in (LANGUAGES, EXTRA_TARGETS):
        for code, (lang_name, _) in table.items():
            if low == code.lower() or low == lang_name.lower():
                return code
    return None


def label(code: str) -> str:
    return f"{name(code)} ({code})"


def source_choices():
    """Languages Whisper can transcribe."""
    langs = sorted(LANGUAGES, key=name)
    return ["Auto-detect (auto)"] + [label(c) for c in langs]


def target_choices():
    """Languages NLLB can translate into."""
    langs = [c for c in LANGUAGES if LANGUAGES[c][1]] + list(EXTRA_TARGETS)
    return ["No translation (none)"] + [label(c) for c in sorted(langs, key=name)]
