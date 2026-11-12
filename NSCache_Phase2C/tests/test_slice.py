"""512KiB-only scope, raw evidence, precision and preservation tests; no extra model runs."""
import csv,hashlib,importlib.util,io,json,re,shutil,subprocess,sys,tempfile,unittest
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

class SliceTests(unittest.TestCase):
 def test_integer_kb_parser_and_exact_matrix(self):
  src=(P/'NSCache_Experiment_DB/source/InputParameter.cpp').read_text()
  branch=src[src.index('if (!strncmp("-Capacity (KB)"'):src.index('if (!strncmp("-Capacity (MB)"')]
  self.assertIn('sscanf(line, "-Capacity (KB): %ld", &cap)',branch);self.assertIn('capacity = cap * 1024;',branch)
  cases=analysis.validate_matrix();self.assertEqual(len(cases),8)
  for c in cases:
   self.assertEqual(c['capacity_bytes'],512*1024);raw=(R/c['config']).read_bytes()
   source=(P/c['source_config']).read_bytes()
   self.assertEqual(raw,source.replace(b'-Capacity (MB): 1',b'-Capacity (KB): 512'))
   self.assertNotIn(b'-Capacity (MB): 0.5',raw)
 def test_eight_actual_attempts_smoke_included_and_concurrency(self):
  meta=[json.loads(p.read_text()) for p in (R/'logs').glob('*/*/metadata.json')]
  self.assertEqual(len(meta),8);self.assertEqual(len({x['run_id'] for x in meta}),8)
  self.assertEqual(sum(x['node_nm']==7 and x['objective']=='ReadLatency' for x in meta),1)
  events=[]
  for m in meta:
   self.assertEqual(m['status'],'FINISHED');self.assertEqual(m['returncode'],0)
   events.extend([(m['started_utc'],1),(m['finished_utc'],-1)])
  active=peak=0
  for _,d in sorted(events):active+=d;peak=max(peak,active)
  self.assertLessEqual(peak,2)
 def test_unit_conversion_normalization_and_rounding(self):
  new,_=analysis.load()
  for r in new:
   raw=(P/r['stdout']).read_text()
   for op,kind in [('read','Hit'),('write','Write')]:
    value=D(re.search(r'Cache '+kind+r' Dynamic Energy\s*=\s*([\d.]+)nJ',raw).group(1))*1000
    self.assertEqual(D(r[op+'_summary_pj']),value)
    self.assertEqual(D(r[op+'_summary_effective_pj_bit']),value/256)
    self.assertEqual(D(r[op+'_bank_effective_pj_bit']),D(r[op+'_bank_sum_pj'])/256)
    self.assertLessEqual(abs(D(r[op+'_rounding_delta_bank_minus_summary_pj'])),D('.501'))
 def test_routing_is_subset_not_additive_total(self):
  new,old=analysis.load()
  for r in new+old:
   if r['status']!='FINISHED':continue
   for op in ('read','write'):
    total=D(r[op+'_bank_sum_pj']);route=D(r[op+'_routing_pj'])
    self.assertEqual(total,D(r[op+'_data_bank_pj'])+D(r[op+'_tag_bank_pj']))
    self.assertEqual(total,route+D(r[op+'_nonrouting_residual_pj']));self.assertLessEqual(route,total)
 def test_matched_precision_sf_and_capacity_ratios(self):
  new,old=analysis.load()
  for r in analysis.scaling(new):
   for precision in ('summary','bank_sum'):
    self.assertEqual(D(r[precision+'_sf']),D(r[precision+'_to_pj'])/D(r[precision+'_from_pj']))
  for r in analysis.ratios(new,old):
   for precision in ('summary','bank_sum'):
    self.assertEqual(D(r[precision+'_ratio']),D(r[precision+'_512_pj'])/D(r[precision+'_1mib_pj']))
 def test_missing_historical_8mib_not_interpolated(self):
  new,old=analysis.load();self.assertEqual(len(new+old),32)
  missing=[r for r in old if r['status']=='MISSING_NOT_RUN'];self.assertEqual(len(missing),4)
  for r in missing:self.assertIn(r['node_nm'],(14,3));self.assertEqual(r['capacity_kib'],8192);self.assertNotIn('read_summary_pj',r)
 def test_missing_new_run_is_not_zero_or_pass(self):
  with tempfile.TemporaryDirectory() as d:
   r=analysis.case_record('missing',7,'ReadLatency',512,R/'configs/L2_7nm_512KiB_ReadLatency.cfg',Path(d),'new_phase2c')
   self.assertEqual(r['status'],'UNRUN');self.assertNotIn('read_summary_pj',r)
 def test_resume_idempotent_without_process_launch(self):
  c=analysis.validate_matrix()[0];before=list((R/'logs'/c['run_id']).glob('*'))
  with patch.object(runner.subprocess,'Popen',side_effect=AssertionError('must not run')),redirect_stdout(io.StringIO()):self.assertEqual(runner.run(c,1800)['status'],'FINISHED')
  self.assertEqual(before,list((R/'logs'/c['run_id']).glob('*')))
 def test_historical_source_cells_and_binary(self):
  self.assertEqual(analysis.protected(),576);self.assertEqual(manifest.verify_inputs(True),576)
  self.assertEqual(len(json.loads((R/'provenance/source_identity.json').read_text())['files']),54)

class TemporaryEvidenceTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.repo=Path(self.temp.name);self.root=self.repo/'NSCache_Phase2C'
  shutil.copytree(R,self.root,ignore=shutil.ignore_patterns('build','runtime','__pycache__'))
  for n in json.loads((R/'provenance/protected.json').read_text())['sha256']:
   dest=self.repo/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(P/n,dest)
  self.stack=[patch.object(analysis,'R',self.root),patch.object(analysis,'P',self.repo),patch.object(common,'P',self.repo)]
  for p in self.stack:p.start()
 def tearDown(self):
  for p in reversed(self.stack):p.stop()
  self.temp.cleanup()
 def execute(self):
  with redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):return analysis.main()
 def outputs(self):
  return {str(p.relative_to(self.root)):p.read_bytes() for p in (self.root/'results').glob('*') if p.is_file()}|{'report':(self.root/'reports/experiment_report.md').read_bytes()}
 def test_regenerate_from_raw_without_binary_and_repeat(self):
  shutil.rmtree(self.root/'results');(self.root/'results').mkdir()
  (self.root/'reports/experiment_report.md').unlink()
  self.assertFalse((self.root/'build/nsc').exists());self.assertEqual(self.execute(),0);first=self.outputs();self.assertEqual(self.execute(),0);self.assertEqual(first,self.outputs())
 def test_tampered_raw_rejected_without_overwriting_outputs(self):
  self.assertEqual(self.execute(),0);before=self.outputs();log=next((self.root/'logs').glob('*/*/stdout.log'));log.write_text('tampered')
  self.assertEqual(self.execute(),2);self.assertEqual(before,self.outputs())
 def test_failed_attempt_has_no_energy(self):
  path=next((self.root/'logs').glob('*/*/metadata.json'));m=json.loads(path.read_text());m.update(status='FAILED',returncode=7);path.write_text(json.dumps(m))
  self.assertEqual(self.execute(),1)
  with (self.root/'results/slice_512kib_energy.csv').open() as f:rows=list(csv.DictReader(f))
  failed=[r for r in rows if r['status']=='FAILED'];self.assertEqual(len(failed),1);self.assertEqual(failed[0]['read_summary_pj'],'')
 def test_manifest_detects_artifact_corruption(self):
  with patch.object(manifest,'R',self.root),patch.object(manifest,'P',self.repo):
   manifest.snapshot();manifest.snapshot(check=True)
   out=self.root/'results/slice_512kib_scaling.csv';out.write_text('corrupted')
   with self.assertRaises(ValueError):manifest.snapshot(check=True)

if __name__=='__main__':unittest.main()
