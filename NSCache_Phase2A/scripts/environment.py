"""Public tool metadata and the actual Phase 2 build recipe; no process env dump."""
import json
from pathlib import Path
import platform
import subprocess
import sys
root=Path(__file__).resolve().parents[1]
cmd=lambda *args:subprocess.check_output(args,text=True).strip()
print(json.dumps(dict(platform=platform.platform(),machine=platform.machine(),python=platform.python_version(),
    compiler=cmd('g++','--version'),make=cmd('make','--version'),
    repository_base_commit=cmd('git','-C',str(root.parent),'rev-parse','HEAD'),
    build_command=f'make -C ../NSCache_Experiment_DB/source -j {int(sys.argv[1]) if len(sys.argv)>1 else 2} target={root}/build/nsc OUTDIR={root}/build/obj',
    flags='-std=c++17 -Wall -O3 -mtune=native; unmodified Phase 1 source/Makefile'),indent=2))
