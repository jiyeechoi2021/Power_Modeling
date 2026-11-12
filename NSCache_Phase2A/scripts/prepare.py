"""Copy Phase 1 width-aligned configs, changing only WordWidth; preserve source bytes."""
from pathlib import Path
import difflib
import hashlib
import json
ROOT=Path(__file__).resolve().parents[1]
P1=ROOT.parent/'NSCache_Experiment_DB'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def prepare():
    rows=[]
    for cache in ('L1','L2'):
        for opt in ('ReadLatency','ReadDynamicEnergy'):
            for node in (14,7,5,3):
                name=f'{cache}_{node}nm'+('_ReadEnergy' if opt=='ReadDynamicEnergy' else '')
                suite='diagnostic_512bit' if node==7 else 'study_reconstructed'
                source=P1/'configs'/suite/(name+'.cfg')
                raw=source.read_bytes()
                assert raw.count(b'-WordWidth (bit): 512')==1
                derived=raw.replace(b'-WordWidth (bit): 512',b'-WordWidth (bit): 256')
                target=ROOT/'configs/phase2_256bit'/(name+'.cfg')
                if target.exists() and target.read_bytes()!=derived:raise ValueError(f'preserve existing config {target}')
                target.write_bytes(derived)
                if node==7:
                    assert derived==(P1/'configs/study_reconstructed'/(name+'.cfg')).read_bytes()
                rows.append(dict(run_id=name,source=str(source.relative_to(ROOT.parent)),source_sha256=sha(source),
                    config=str(target.relative_to(ROOT)),config_sha256=sha(target),
                    change='WordWidth (bit): 512 -> 256 only',
                    diff=''.join(difflib.unified_diff(raw.decode().splitlines(True),derived.decode().splitlines(True),fromfile=str(source.relative_to(ROOT.parent)),tofile=str(target.relative_to(ROOT))))))
    (ROOT/'provenance/configuration_derivation.json').write_text(json.dumps(rows,indent=2)+'\n')
    print(f'Prepared {len(rows)} 256bit inputs; existing 7nm inputs byte-identical, to be freshly executed')

if __name__=='__main__':prepare()
