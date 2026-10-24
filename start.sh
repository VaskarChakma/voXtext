#!/usr/bin/env bash
cd "$(dirname "$0")"
[ -d .venv ] || { echo "Please run ./setup.sh first."; exit 1; }
source .venv/bin/activate

# On Linux, let CTranslate2 find pip-installed NVIDIA libraries.
NV_LIBS=$(python - <<'EOF' 2>/dev/null
import glob, os, site
dirs = [d for p in site.getsitepackages() for d in glob.glob(os.path.join(p, "nvidia", "*", "lib"))]
print(":".join(dirs))
EOF
)
[ -n "$NV_LIBS" ] && export LD_LIBRARY_PATH="$NV_LIBS${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
python app.py
