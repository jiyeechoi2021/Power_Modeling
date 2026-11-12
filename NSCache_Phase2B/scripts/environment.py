"""Capture safe public runtime/build metadata for future reproductions."""
import json,platform,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1]
c=lambda *a:subprocess.check_output(a,text=True).strip()
print(json.dumps(dict(platform=platform.platform(),python=platform.python_version(),compiler=c('g++','--version'),make=c('make','--version'),repository_commit=c('git','rev-parse','HEAD'),command=f'make -C ../NSCache_Experiment_DB/source -j 2 target={R}/build/nsc OUTDIR={R}/build/obj',flags='-std=c++17 -Wall -O3 -mtune=native'),indent=2))
