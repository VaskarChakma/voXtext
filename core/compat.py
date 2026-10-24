"""Small fixes for third-party quirks. Imported automatically by the core package."""

import os
from pathlib import Path

os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")


def patch_pyav():
    """PyAV 19+ removed the 'metadata_errors' option that faster-whisper passes.
    Retry without it so any PyAV version works."""
    try:
        import av
    except ImportError:
        return
    if getattr(av.open, "_patched", False):
        return
    original = av.open

    def safe_open(*args, **kwargs):
        try:
            return original(*args, **kwargs)
        except TypeError as e:
            if "metadata_errors" in str(e) and "metadata_errors" in kwargs:
                kwargs.pop("metadata_errors")
                return original(*args, **kwargs)
            raise

    safe_open._patched = True
    av.open = safe_open


def add_nvidia_dll_paths():
    """On Windows, pip-installed NVIDIA libraries (cuBLAS, cuDNN) live in
    site-packages/nvidia/*/bin, which Windows doesn't search by default."""
    if os.name != "nt":
        return
    import site
    import sysconfig
    roots = set(site.getsitepackages() + [sysconfig.get_paths()["purelib"]])
    for root in roots:
        for bin_dir in (Path(root) / "nvidia").glob("*/bin"):
            try:
                os.add_dll_directory(str(bin_dir))
            except (OSError, AttributeError):
                pass
            os.environ["PATH"] = str(bin_dir) + os.pathsep + os.environ.get("PATH", "")


GPU_ERROR_HINTS = ("cublas", "cudnn", "cudart", "cuda")
GPU_FALLBACK_MSG = ("GPU libraries could not be loaded, so switching to CPU (slower). "
                    "To use your NVIDIA GPU, run: "
                    "pip install nvidia-cublas-cu12 \"nvidia-cudnn-cu12==9.*\"")


def is_gpu_error(err: Exception) -> bool:
    return isinstance(err, RuntimeError) and any(k in str(err).lower() for k in GPU_ERROR_HINTS)


def pick_device(device: str = "auto") -> str:
    if device != "auto":
        return device
    try:
        import ctranslate2
        if ctranslate2.get_cuda_device_count() > 0:
            return "cuda"
    except Exception:
        pass
    return "cpu"


patch_pyav()
add_nvidia_dll_paths()
