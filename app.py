"""
voXtext web app. Runs entirely on your computer at http://127.0.0.1:7860
Start with:  python app.py   (or the start script for your OS)
"""

import os
import tempfile
from pathlib import Path

os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")

import gradio as gr

from core import __version__
from core import languages as L
from core.engine import Engine
from core.subtitles import FORMAT_HELP, FORMATS
from core.transcriber import WHISPER_MODELS, find_media
from core.translator import DEFAULT_NLLB, NLLB_MODELS, is_installed

engine = Engine()
PREVIEW_LIMIT = 20000


def _upload_paths(uploads):
    return [Path(u if isinstance(u, str) else u.name) for u in (uploads or [])]


def run(uploads, folder_path, source_label, target_label, formats, whisper_model,
        nllb_model, device, prompt, save_next, progress=gr.Progress()):
    uploaded = _upload_paths(uploads)
    files = list(uploaded)
    if folder_path and folder_path.strip():
        files += find_media([folder_path])
    if not files:
        raise gr.Error("Add a video first: upload one, or paste a file/folder path.")
    if not formats:
        raise gr.Error("Pick at least one output format.")

    source = L.resolve(source_label) or L.AUTO
    target = L.resolve(target_label) or L.NONE
    if target != L.NONE and not is_installed(nllb_model):
        raise gr.Error(f"The translation model '{nllb_model}' isn't installed yet. "
                       f"Run once with internet:  python download_models.py --nllb {nllb_model}")

    def warn(msg):
        print(f"[warning] {msg}")
        gr.Warning(msg)

    engine.on_warning = warn
    engine.configure(whisper_model, nllb_model, device)
    progress(0, desc="Loading models (the first run takes a moment)...")

    out_tmp = Path(tempfile.mkdtemp(prefix="subtitles_"))
    outputs, originals, translations, summary = [], [], [], []
    for i, f in enumerate(files):
        out_dir = f.parent if (save_next and f not in uploaded) else out_tmp

        def cb(frac, msg, i=i, name=f.name):
            progress((i + frac) / len(files), desc=f"[{i + 1}/{len(files)}] {name} · {msg}")

        r = engine.process(f, out_dir, source, target, formats, prompt=prompt,
                           progress_cb=cb)
        outputs += [str(p) for p in r["files"]]
        summary.append(f"✅ {r['summary']}")
        summary += [f"ℹ️ {n}" for n in r["notes"]]
        originals.append(f"===== {f.name} =====\n" + "\n".join(s["text"] for s in r["segments"]))
        if r["target"]:
            translations.append(f"===== {f.name} =====\n"
                                + "\n".join(s["translation"] for s in r["segments"]))

    def clip(parts):
        text = "\n\n".join(parts)
        if len(text) > PREVIEW_LIMIT:
            text = text[:PREVIEW_LIMIT] + "\n\n… (preview shortened; download the files for everything)"
        return text

    return outputs, "\n\n".join(summary), clip(originals), clip(translations)


CSS = """
#title {text-align:center; margin-bottom:0}
#subtitle {text-align:center; opacity:.75; margin-top:4px}
footer {visibility:hidden}
"""

with gr.Blocks(title="voXtext", theme=gr.themes.Soft(primary_hue="indigo"), css=CSS) as demo:
    gr.Markdown("# 🎬 voXtext", elem_id="title")
    gr.Markdown("Transcribe and translate videos between 100+ languages, "
                "**fully offline**. Your files never leave this computer.",
                elem_id="subtitle")

    with gr.Row(equal_height=False):
        with gr.Column(scale=5):
            with gr.Tab("Upload"):
                uploads = gr.File(label="Video or audio files", file_count="multiple")
            with gr.Tab("File / folder path (best for large files)"):
                folder = gr.Textbox(label="Path on this computer",
                                    placeholder=r"D:\Videos\lectures   or   /home/me/videos/talk.mp4")
                save_next = gr.Checkbox(value=True, label="Save subtitles next to the original videos")

            with gr.Row():
                source = gr.Dropdown(L.source_choices(), value="Auto-detect (auto)",
                                     label="🎙️ Spoken language", filterable=True)
                target = gr.Dropdown(L.target_choices(), value="No translation (none)",
                                     label="🌐 Translate to", filterable=True)

            formats = gr.CheckboxGroup(
                FORMATS, value=["txt", "srt", "bilingual"], label="Output files",
                info=" · ".join(f"{k}: {v}" for k, v in FORMAT_HELP.items()))

            with gr.Accordion("Advanced settings", open=False):
                with gr.Row():
                    whisper_model = gr.Dropdown(WHISPER_MODELS, value="large-v3",
                                                label="Speech model (Whisper)")
                    nllb_model = gr.Dropdown(list(NLLB_MODELS), value=DEFAULT_NLLB,
                                             label="Translation model (NLLB)")
                    device = gr.Dropdown(["auto", "cuda", "cpu"], value="auto", label="Device")
                prompt = gr.Textbox(label="Hint: names or terms that appear in the video",
                                    placeholder="e.g. Kim Min-su, Kubernetes, Seoul National University")

            run_btn = gr.Button("▶  Start", variant="primary", size="lg")

        with gr.Column(scale=6):
            status = gr.Markdown("Results will appear here.")
            out_files = gr.File(label="Download subtitles & transcripts")
            with gr.Tab("Original"):
                original_box = gr.Textbox(lines=18, show_label=False, show_copy_button=True)
            with gr.Tab("Translation"):
                translation_box = gr.Textbox(lines=18, show_label=False, show_copy_button=True)

    gr.Markdown(f"<center><sub>voXtext v{__version__} · Whisper + NLLB-200 · "
                "100% local</sub></center>")

    run_btn.click(
        run,
        [uploads, folder, source, target, formats, whisper_model, nllb_model, device,
         prompt, save_next],
        [out_files, status, original_box, translation_box],
    )

if __name__ == "__main__":
    demo.queue().launch(server_name="127.0.0.1", inbrowser=True)
