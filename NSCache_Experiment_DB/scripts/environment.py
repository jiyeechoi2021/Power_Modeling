"""Record public tool/platform metadata only; never dump environment variables."""
import json
import platform
import subprocess

def command(*args):
    return subprocess.check_output(args, text=True).strip()

if __name__ == '__main__':
    print(json.dumps({
        'platform': platform.platform(), 'machine': platform.machine(),
        'python': platform.python_version(), 'compiler': command('g++', '--version'),
        'make': command('make', '--version'),
        'repository_base_commit': command('git', 'rev-parse', 'HEAD'),
        'build_command': 'make -C source -j 2 target=../build/nsc OUTDIR=../build/obj',
        'flags': '-std=c++17 -Wall -O3 -mtune=native; GNU Makefile unmodified',
    }, indent=2))
