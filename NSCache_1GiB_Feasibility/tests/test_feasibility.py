"""Independent raw arithmetic, preservation, failure and reproducibility checks."""
import csv,io,json,math,re,shutil,sys,tempfile,unittest
from contextlib import redirect_stdout,redirect_stderr
from decimal import Decimal as D
from pathlib import Path
from unittest.mock import patch
R=Path(__file__).resolve().parents[1];P=R.parent
sys.path.insert(0,str(R/'scripts'))
import analyze as analysis
import common,manifest,run as runner

class ActualEvidenceTests(unittest.TestCase):
 def test_capacity_only_four_primary_inputs(self):
  cases=json.loads((R/'provenance/cases.json').read_text());primary=[c for c in cases if c['capacity_mib']==1024]
  self.assertEqual({(c['node_nm'],c['objective']) for c in primary},{(n,o) for n in (3,7) for o in ('ReadLatency','ReadDynamicEnergy')})
  for c in cases:
   self.assertEqual((R/c['config']).read_bytes(),(P/c['source_config']).read_bytes().replace(f"-Capacity (MB): {c['baseline_capacity_mib']}".encode(),f"-Capacity (MB): {c['capacity_mib']}".encode()))
   self.assertEqual(c['capacity_bytes'],c['capacity_mib']*1024**2)
   self.assertEqual(c['width_bits'],256)
 def test_actual_terminal_execution_and_order(self):
  paths=list((R/'logs').glob('*/*/metadata.json'));meta=[json.loads(p.read_text()) for p in paths]
  primary=[m for m in meta if m['capacity_mib']==1024];self.assertEqual(len(primary),4)
  self.assertLessEqual(max(m['finished_utc'] for m in primary if m['node_nm']==3),min(m['started_utc'] for m in primary if m['node_nm']==7))
  for m,p in zip(meta,paths):
   self.assertIn(m['status'],('FINISHED','FAILED','TIMEOUT'));self.assertGreater(m['max_rss_kib'],0)
   self.assertEqual(m['timeout_seconds'],1800)
   if m['status']=='FINISHED':self.assertEqual(m['returncode'],0);self.assertIn('Finished!',(p.parent/'stdout.log').read_text())
 def test_actual_concurrency_limit(self):
  events=[]
  for p in (R/'logs').glob('*/*/metadata.json'):
   m=json.loads(p.read_text());events.extend([(m['started_utc'],1),(m['finished_utc'],-1)])
  active=peak=0
  for _,delta in sorted(events):active+=delta;peak=max(peak,active)
  self.assertLessEqual(peak,2);self.assertEqual(active,0)
 def test_bank_resolution_follows_printed_unit(self):
  for r in analysis.load():
   if r['status']!='FINISHED':continue
   raw=(P/r['stdout']).read_text();sections=re.split(r'CACHE (?:DATA|TAG) ARRAY DETAILS',raw)[1:]
   for label,section in zip(('data','tag'),sections):
    for op,title in [('read','Read'),('write','Write')]:
     m=re.search(r'-\s*'+title+r' Dynamic Energy\s*=\s*([\d.]+)(pJ|nJ|fJ)',section)
     resolution=D(10)**(-len(m.group(1).partition('.')[2]))*{'pJ':D(1),'nJ':D(1000),'fJ':D('.001')}[m.group(2)]
     self.assertEqual(resolution,D(r[op+'_'+label+'_bank_resolution_pj']))
 def test_four_historical_baselines_not_rerun(self):
  rows=analysis.load();base=[r for r in rows if r['origin']=='verified_historical_raw'];self.assertEqual(len(base),4)
  self.assertEqual({(r['node_nm'],r['capacity_mib']) for r in base},{(3,128),(7,32)})
  for r in base:self.assertEqual(r['status'],'FINISHED');self.assertNotIn('NSCache_1GiB_Feasibility/logs',r['stdout'])
 def test_independent_units_and_data_capacity(self):
  for r in analysis.load():
   if r['status']!='FINISHED':continue
   raw=(P/r['stdout']).read_text()
   for op,label in [('read','Hit'),('write','Write')]:
    value=D(re.search(r'Cache '+label+r' Dynamic Energy\s*=\s*([\d.]+)nJ',raw).group(1))*1000
    self.assertEqual(value,D(r[op+'_summary_pj']));self.assertEqual(value/256,D(r[op+'_summary_effective_pj_bit']))
   dims=[int(v) for k in ('bank','subarray','mat') for v in re.findall(r'\d+',r['organization']['data'][k])]
   self.assertEqual(math.prod(dims)//8,r['capacity_bytes']);self.assertGreater(D(r['write_latency_ns']),0)
 def test_hierarchy_not_double_counted(self):
  for r in analysis.load():
   if r['status']!='FINISHED':continue
   for op in ('read','write'):
    self.assertEqual(D(r[op+'_bank_sum_pj']),D(r[op+'_data_bank_pj'])+D(r[op+'_tag_bank_pj']))
    self.assertEqual(D(r[op+'_bank_sum_pj']),D(r[op+'_routing_pj'])+D(r[op+'_nonrouting_residual_pj']))
    self.assertLessEqual(abs(D(r[op+'_rounding_delta_bank_minus_summary_pj'])),D(r[op+'_summary_bank_difference_bound_pj']))
    self.assertEqual(D(r[op+'_summary_bank_difference_bound_pj']),D('.5')+(D(r[op+'_data_bank_resolution_pj'])+D(r[op+'_tag_bank_resolution_pj']))/2)
 def test_sf_and_capacity_ratio_from_raw_same_precision(self):
  rows=analysis.load();sf,paper,capacity=analysis.comparisons(rows);self.assertEqual(len(sf),8)
  by={(r['node_nm'],r['capacity_mib'],r['objective']):r for r in rows}
  for r in sf:
   if r['status']=='UNAVAILABLE':self.assertIsNone(r['model_sf_7_to_3']);continue
   k=r['operation']+'_'+r['precision']+'_pj';a,b=by[7,1024,r['objective']],by[3,1024,r['objective']]
   self.assertEqual(D(r['model_sf_7_to_3']),D(b[k])/D(a[k]));self.assertEqual(D(r['reported_reference_sf']),D('2.420')/D('2.780'))
  for r in capacity:
   if r['status']=='VALID':self.assertEqual(D(r['capacity_energy_ratio']),D(r['target_pj'])/D(r['baseline_pj']))
  for r in paper:self.assertEqual(r['reference_operation'],'unconfirmed')
 def test_completed_resume_without_process(self):
  cases=json.loads((R/'provenance/cases.json').read_text());before=len(list((R/'logs').glob('*/*/metadata.json')))
  for c in cases:
   p=sorted((R/'logs'/c['run_id']).glob('*/metadata.json'))[-1]
   if json.loads(p.read_text())['status']=='FINISHED':
    with patch.object(runner.subprocess,'Popen',side_effect=AssertionError('resume cannot launch')),redirect_stdout(io.StringIO()):self.assertEqual(runner.run(c,1800)['status'],'FINISHED')
  self.assertEqual(before,len(list((R/'logs').glob('*/*/metadata.json'))))
 def test_history_source_cell_binary_and_no_fitting(self):
  self.assertEqual(manifest.verify_inputs(True),686)
  for name in ('prepare.py','run.py'):
   s=(R/'scripts'/name).read_text()
   for ref in ('2.780','2.420','0.8705'):self.assertNotIn(ref,s)

class TemporaryEvidenceTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.repo=Path(self.temp.name);self.root=self.repo/R.name
  shutil.copytree(R,self.root,ignore=shutil.ignore_patterns('build','runtime','__pycache__'))
  for n in json.loads((R/'provenance/protected.json').read_text())['sha256']:
   p=self.repo/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(P/n,p)
  self.patches=[patch.object(analysis,'R',self.root),patch.object(analysis,'P',self.repo),patch.object(common,'P',self.repo),patch.object(manifest,'R',self.root),patch.object(manifest,'P',self.repo)]
  for p in self.patches:p.start()
 def tearDown(self):
  for p in reversed(self.patches):p.stop()
  self.temp.cleanup()
 def execute(self):
  with redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):return analysis.main()
 def outputs(self):return {str(p.relative_to(self.root)):p.read_bytes() for p in (self.root/'results').glob('*') if p.is_file()}|{'report':(self.root/'reports/experiment_report.md').read_bytes()}
 def test_raw_regeneration_determinism_without_binary(self):
  shutil.rmtree(self.root/'results');(self.root/'results').mkdir();(self.root/'reports/experiment_report.md').unlink()
  self.assertFalse((self.root/'build/nsc').exists());self.assertEqual(self.execute(),0);a=self.outputs();self.assertEqual(self.execute(),0);self.assertEqual(a,self.outputs())
 def test_corruption_rejected_before_outputs_change(self):
  self.assertEqual(self.execute(),0);old=self.outputs();p=next((self.root/'logs').glob('*/*/stdout.log'));p.write_text('corrupt')
  self.assertEqual(self.execute(),2);self.assertEqual(old,self.outputs())
 def test_failed_or_timeout_no_energy_or_sf_fabricated(self):
  p=next((self.root/'logs').glob('*/*/metadata.json'));m=json.loads(p.read_text());m.update(status='TIMEOUT',returncode=-9);p.write_text(json.dumps(m))
  self.assertEqual(self.execute(),0) # successful analysis with explicit failed experiment
  with (self.root/'results/energy_results.csv').open() as f:rows=list(csv.DictReader(f))
  r=next(r for r in rows if r['status']=='TIMEOUT');self.assertEqual(r['read_summary_pj'],'');self.assertEqual(r['write_summary_pj'],'')
  with (self.root/'results/cross_node_sf.csv').open() as f:sf=list(csv.DictReader(f))
  for r in sf:
   if r['objective']==m['objective']:self.assertEqual(r['status'],'UNAVAILABLE');self.assertEqual(r['model_sf_7_to_3'],'')
 def test_manifest_detects_tamper(self):
  manifest.snapshot();manifest.snapshot(check=True)
  (self.root/'results/energy_results.csv').write_text('changed')
  with self.assertRaises(ValueError):manifest.snapshot(check=True)

if __name__=='__main__':unittest.main()
