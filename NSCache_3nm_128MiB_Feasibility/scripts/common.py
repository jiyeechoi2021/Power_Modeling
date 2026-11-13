"""Raw parser reused from verified Phase 1/2-A, retained locally for Phase 2-C."""
import re
from decimal import Decimal
D=Decimal
NUMBER=r'([0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?)'
METRICS={
 'read_pj_per_access':(r'^\s*- Cache Hit Dynamic Energy\s*=\s*'+NUMBER+r'nJ per access',Decimal(1000),Decimal('.5')),
 'write_pj_per_access':(r'^\s*- Cache Write Dynamic Energy\s*=\s*'+NUMBER+r'nJ per access',Decimal(1000),Decimal('.5')),
 'leakage_mw':(r'^\s*- Cache Total Leakage Power\s*=\s*'+NUMBER+r'mW',Decimal(1),Decimal('.0005')),
 'hit_latency_ns':(r'^\s*- Cache Hit Latency\s*=\s*'+NUMBER+r'ns',Decimal(1),Decimal('.0005')),
 'area_mm2':(r'^\s*- Total Area\s*=\s*'+NUMBER+r'mm\^2',Decimal(1),Decimal('.0005')),
 'feasible_solutions':(r'^numSolutions\s*=\s*(\d+)',Decimal(1),Decimal(0)),
}

def parse(raw):
    values={}
    for field,(pattern,mult,tol) in METRICS.items():
        matches=re.findall(pattern,raw,re.M)
        if len(matches)!=1: raise ValueError(f'{field}: expected 1 summary, found {len(matches)}')
        values[field]=Decimal(matches[0])*mult
    blocks=re.findall(r'\n\s*CONFIGURATION\s*\n\s*=+\n(.*?)\n\s*=+\n\s*RESULT',raw,re.S)
    if len(blocks)!=2: raise ValueError(f'expected data/tag configuration blocks, got {len(blocks)}')
    organizations = {}
    for label, block in zip(('data', 'tag'), blocks):
        organization = {'raw_configuration': block.strip()}
        for field, pattern in [('bank', r'Bank Organization:\s*(\d+ x \d+)'),
                               ('subarray', r'SubArray Organization:\s*(\d+ x \d+)'),
                               ('mat', r'Mat Size\s*:\s*(\d+ Rows x \d+ Columns)')]:
            match = re.search(pattern, block)
            if not match:
                raise ValueError(f'{label}: missing {field} organization')
            organization[field] = match.group(1)
        organizations[label] = organization
    return values,organizations

def require(ok,message):
    if not ok:raise ValueError(message)

def breakdown(raw):
    """Preserve printed detail and per-subarray/per-mat scope; do not sum nested levels."""
    sections=re.split(r'CACHE (?:DATA|TAG) ARRAY DETAILS',raw)
    require(len(sections)==3,'missing data/tag detail sections')
    result={}
    for label,text in zip(('data','tag'),sections[1:]):
        power=text.split('    Power:',1)[1]
        read,write=power.split('     - Write Dynamic Energy = ',1)
        orgtext=text.split('CONFIGURATION',1)[1].split('RESULT',1)[0]
        entry={'configuration_detail':orgtext.strip(),'read':{},'write':{}}
        for kind,block in [('read',read),('write','     - Write Dynamic Energy = '+write)]:
            for line in block.splitlines():
                m=re.search(r'([A-Za-z][A-Za-z &-]*Dynamic Energy)\s*=\s*([\d.]+)(pJ|nJ|fJ)(.*)',line)
                if m:
                    key=m.group(1).strip()
                    value=D(m.group(2))*{'pJ':D(1),'nJ':D(1000),'fJ':D('.001')}[m.group(3)]
                    entry[kind][key]={'pj':str(value),'scope':m.group(4).strip() or 'as printed; see raw hierarchy'}
        for kind in ('read','write'):
            key='Read Dynamic Energy' if kind=='read' else 'Write Dynamic Energy'
            require(key in entry[kind],f'missing {label} {kind} bank energy')
        result[label]=entry
    return result

import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def energy(values,org,detail):
 result={k:str(v) for k,v in values.items()}
 for op,metric in [('read','read_pj_per_access'),('write','write_pj_per_access')]:
  label='Read Dynamic Energy' if op=='read' else 'Write Dynamic Energy'
  data=D(detail['data'][op][label]['pj']);tag=D(detail['tag'][op][label]['pj']);route=sum(D(detail[a][op]['H-Tree Dynamic Energy']['pj']) for a in ('data','tag'));total=data+tag
  require(0<=route<=total,'routing outside bank total')
  result.update({op+'_summary_pj':str(values[metric]),op+'_summary_effective_pj_bit':str(values[metric]/256),op+'_bank_sum_pj':str(total),op+'_bank_effective_pj_bit':str(total/256),op+'_rounding_delta_bank_minus_summary_pj':str(total-values[metric]),op+'_data_bank_pj':str(data),op+'_tag_bank_pj':str(tag),op+'_routing_pj':str(route),op+'_nonrouting_residual_pj':str(total-route)})
  require(abs(total-values[metric])<=D('.501'),'summary/bank precision inconsistency')
 return result

def read_raw(meta_path,config,cell,origin):
 m=json.loads(meta_path.read_text());out=meta_path.parent/'stdout.log';err=meta_path.parent/'stderr.log'
 for p,k in [(config,'config_sha256'),(cell,'cell_sha256'),(out,'stdout_sha256'),(err,'stderr_sha256')]:require(sha(p)==m[k],f'hash mismatch {p}')
 if 'environment_sha256' in m:require(sha(meta_path.parent/'environment.json')==m['environment_sha256'],'environment hash mismatch')
 raw=out.read_text();status=m['status']
 base=dict(origin=origin,status=status,returncode=m.get('returncode'),elapsed_seconds=m.get('elapsed_seconds'),max_rss_kib=m.get('max_rss_kib'),metadata=str(meta_path.relative_to(P)),config=str(config.relative_to(P)),stdout=str(out.relative_to(P)),stderr=str(err.relative_to(P)),binary_sha256=m['binary_sha256'],config_sha256=m['config_sha256'],stdout_sha256=m['stdout_sha256'])
 if status=='FINISHED':
  require(m['returncode']==0 and 'Finished!' in raw,'invalid completion');values,org=parse(raw);detail=breakdown(raw);base.update(energy(values,org,detail),organization=org,breakdown=detail,analysis_status='VALID')
 else:
  base.update(analysis_status='UNSUPPORTED_GEOMETRY' if 'capacity violation' in raw else status,error='capacity violation' if 'capacity violation' in raw else 'see raw output')
 return base
