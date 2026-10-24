# Contributing

Thanks for your interest in improving voXtext! Bug reports, translations of the docs, and code contributions are all welcome.

## Reporting a bug

Open an [issue](https://github.com/VaskarChakma/voXtext/issues) and include:

- Your OS, Python version and GPU (if any)
- What you ran, and the **full error log** from the terminal window
- The video's spoken language and length, if relevant

## Suggesting a feature

Open an issue describing the problem you'd like solved. Concrete examples ("I want to batch-translate a folder of Japanese lectures into Spanish") help a lot.

## Submitting code

1. Fork the repo and create a branch: `git checkout -b my-feature`
2. Set up with `setup_windows.bat` or `./setup.sh`
3. Keep changes focused; follow the existing style (plain Python, no extra frameworks)
4. Check that the app starts and `python cli.py --help` still works
5. Open a pull request describing what changed and why

## Project layout

```
app.py              Web interface (Gradio)
cli.py              Command-line interface
download_models.py  One-time model download / conversion
core/
  engine.py         Pipeline: transcribe -> translate -> write files
  transcriber.py    Whisper speech-to-text
  translator.py     NLLB-200 translation via CTranslate2
  languages.py      Language names and code mappings
  subtitles.py      TXT / SRT / VTT writers
  compat.py         Workarounds for library quirks (PyAV, Windows CUDA DLLs)
```
