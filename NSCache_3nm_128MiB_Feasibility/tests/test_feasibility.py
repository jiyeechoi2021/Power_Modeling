"""Controlled-capacity, raw arithmetic, timeout/failure evidence and privacy-lineage tests."""
import csv,hashlib,io,json,math,re,shutil,sys,tempfile,unittest
from contextlib import redirect_stdout,redirect_stderr
from decimal import Decimal as D
from pathlib import Path
from unittest.mock import patch
R=Path(__file__).resolve().parents[1];P=R.parent
sys.path.insert(0,str(R/'scripts'))
import analyze as analysis
import common
import run as runner
import manifest

class FeasibilityTests(unittest.TestCase):
 def test_only_capacity_changes_and_two_inherited_objectives(self):
  cases=json.loads((R/'provenance/cases.json').read_text());self.assertEqual(len(cases),2)
  self.assertEqual({x['objective'] for x in cases},{'ReadLatency','ReadDynamicEnergy'})
  for c in cases:
   original=(P/c['source_config']).read_bytes();derived=(R/c['config']).read_bytes()
   self.assertEqual(derived,original.replace(b'-Capacity (MB): 32',b'-Capacity (MB): 128'))
   self.assertEqual(c['capacity_bytes'],128*1024**2);self.assertEqual(c['width_bits'],256)
   self.assertNotIn(b'0.917',derived)
 def test_two_real_completed_attempts(self):
  paths=list((R/'logs').glob('*/*/metadata.json'));self.assertEqual(len(paths),2)
  for p in paths:
   m=json.loads(p.read_text());self.assertEqual(m['status'],'FINISHED');self.assertEqual(m['returncode'],0)
   self.assertIn('Finished!',(p.parent/'stdout.log').read_text());self.assertEqual((p.parent/'stderr.log').stat().st_size,0)
   self.assertGreater(m['max_rss_kib'],0);self.assertLess(m['elapsed_seconds'],1800)
 def test_32mib_is_verified_not_reexecuted(self):
  rows=analysis.load();self.assertEqual(len(rows),4)
  for r in rows:
   if r['capacity_mib']==32:self.assertEqual(r['origin'],'verified_phase2b_raw');self.assertIn('NSCache_Phase2B/logs/',r['stdout'])
 def test_independent_raw_unit_conversion_and_latency(self):
  for r in analysis.load():
   raw=(P/r['stdout']).read_text()
   for op,label in [('read','Hit'),('write','Write')]:
    value=D(re.search(r'Cache '+label+r' Dynamic Energy\s*=\s*([\d.]+)nJ',raw).group(1))*1000
    self.assertEqual(value,D(r[op+'_summary_pj']));self.assertEqual(value/256,D(r[op+'_summary_effective_pj_bit']))
   self.assertGreater(D(r['write_latency_ns']),0)
 def test_physical_data_geometry_matches_capacity(self):
  for r in analysis.load():
   dims=[int(v) for key in ('bank','subarray','mat') for v in re.findall(r'\d+',r['organization']['data'][key])]
   self.assertEqual(math.prod(dims)//8,r['capacity_bytes']);self.assertEqual(r['derived_data_array_bytes'],r['capacity_bytes'])
 def test_no_routing_double_count_and_fine_precision(self):
  for r in analysis.load():
   for op in ('read','write'):
    total=D(r[op+'_bank_sum_pj']);self.assertEqual(total,D(r[op+'_data_bank_pj'])+D(r[op+'_tag_bank_pj']))
    self.assertEqual(total,D(r[op+'_routing_pj'])+D(r[op+'_nonrouting_residual_pj']))
    self.assertEqual(D(r[op+'_bank_effective_pj_bit']),total/256)
    self.assertLessEqual(abs(D(r[op+'_rounding_delta_bank_minus_summary_pj'])),D('.501'))
 def test_capacity_ratios_use_same_precision(self):
  ratios,paper=analysis.compare(analysis.load());self.assertEqual(len(ratios),4)
  for r in ratios:
   for q in ('summary','bank_sum'):self.assertEqual(D(r[q+'_ratio_128_over_32']),D(r[q+'_128_pj'])/D(r[q+'_32_pj']))
  self.assertEqual(len(paper),16)
  for r in paper:
   self.assertEqual(r['status'],'NUMERIC_COMPARISON_ONLY');self.assertEqual(r['reference_operation'],'unconfirmed')
   self.assertEqual(D(r['model_div_reference']),D(r['model_effective_pj_bit'])/D('.917'))
 def test_completed_resume_never_launches_process(self):
  c=json.loads((R/'provenance/cases.json').read_text())[0]
  with patch.object(runner.subprocess,'Popen',side_effect=AssertionError('not allowed')),redirect_stdout(io.StringIO()):self.assertEqual(runner.run(c,1800)['status'],'FINISHED')
  self.assertEqual(len(list((R/'logs').glob('*/*/metadata.json'))),2)
 def test_source_historical_and_binary_hashes(self):self.assertEqual(analysis.protected(),647);self.assertEqual(manifest.verify_inputs(True),647)
 def test_reference_not_used_for_execution_and_author_config_missing(self):
  for name in ('prepare.py','run.py'):
   self.assertNotIn('0.917',(R/'scripts'/name).read_text())
  inv=json.loads((R/'provenance/reference_inventory.json').read_text())
  self.assertEqual(inv['matching_3nm_128MiB_reference_configs'],[]);self.assertIn('unavailable',inv['author_original_config_status'].lower())

class TemporaryEvidenceTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.repo=Path(self.temp.name);self.root=self.repo/R.name
  shutil.copytree(R,self.root,ignore=shutil.ignore_patterns('build','runtime','__pycache__'))
  for n in json.loads((R/'provenance/protected.json').read_text())['sha256']:
   p=self.repo/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(P/n,p)
  self.patches=[patch.object(analysis,'R',self.root),patch.object(analysis,'P',self.repo),patch.object(common,'P',self.repo)]
  for p in self.patches:p.start()
 def tearDown(self):
  for p in reversed(self.patches):p.stop()
  self.temp.cleanup()
 def execute(self):
  with redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):return analysis.main()
 def outputs(self):return {str(p.relative_to(self.root)):p.read_bytes() for p in (self.root/'results').glob('*') if p.is_file()}|{'report':(self.root/'reports/experiment_report.md').read_bytes()}
 def test_raw_only_regeneration_without_binary_is_deterministic(self):
  shutil.rmtree(self.root/'results');(self.root/'results').mkdir();(self.root/'reports/experiment_report.md').unlink()
  self.assertFalse((self.root/'build/nsc').exists());self.assertEqual(self.execute(),0);first=self.outputs();self.assertEqual(self.execute(),0);self.assertEqual(first,self.outputs())
 def test_corrupt_raw_rejected_without_output_mutation(self):
  self.assertEqual(self.execute(),0);old=self.outputs();p=next((self.root/'logs').glob('*/*/stdout.log'));p.write_text('corrupt')
  self.assertEqual(self.execute(),2);self.assertEqual(old,self.outputs())
 def test_timeout_never_fabricates_energy(self):
  p=next((self.root/'logs').glob('*/*/metadata.json'));m=json.loads(p.read_text());m.update(status='TIMEOUT',returncode=-9);p.write_text(json.dumps(m))
  self.assertEqual(self.execute(),1)
  with (self.root/'results/energy_results.csv').open() as f:rows=list(csv.DictReader(f))
  r=next(x for x in rows if x['status']=='TIMEOUT');self.assertEqual(r['read_summary_pj'],'');self.assertEqual(r['write_summary_pj'],'')
 def test_manifest_detects_tampering(self):
  with patch.object(manifest,'R',self.root),patch.object(manifest,'P',self.repo):
   manifest.snapshot();manifest.snapshot(check=True)
   (self.root/'results/energy_results.csv').write_text('changed')
   with self.assertRaises(ValueError):manifest.snapshot(check=True)

if __name__=='__main__':unittest.main()
