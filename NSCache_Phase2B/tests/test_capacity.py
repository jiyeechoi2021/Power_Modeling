"""Raw parsing, precision, algebra, failure handling, resume and preservation regressions."""
import csv,hashlib,importlib.util,io,json,re,subprocess,tempfile,unittest
from contextlib import redirect_stdout,redirect_stderr
from decimal import Decimal as D
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
R=Path(__file__).resolve().parents[1]
def module(name,file):
 s=importlib.util.spec_from_file_location(name,R/'scripts'/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
analysis=module('capacity_analysis','analyze.py');runner=module('capacity_runner','run.py');manifest=module('capacity_manifest','manifest.py')
class CapacityTests(unittest.TestCase):
 def test_raw_parse_units_and_precision(self):
  rows=analysis.load();r=next(x for x in rows if x['node_nm']==14 and x['capacity_mib']==32 and x['objective']=='ReadLatency')
  self.assertEqual(D(r['read_summary_pj']),D(490));self.assertEqual(D(r['read_bank_sum_pj']),D('489.648'))
  self.assertEqual(D(r['read_summary_effective_pj_bit']),D(490)/256)
  self.assertEqual(D(r['read_bank_effective_pj_bit']),D('489.648')/256)
  self.assertNotEqual(r['read_summary_effective_pj_bit'],r['read_bank_effective_pj_bit'])
 def test_unsupported_cases_never_get_energy(self):
  rows=analysis.load();failed=[x for x in rows if x['status']=='FAILED'];self.assertEqual(len(failed),22)
  for x in failed:self.assertNotIn('read_summary_pj',x);self.assertEqual(x['returncode'],255);self.assertEqual(x['analysis_status'],'UNSUPPORTED_GEOMETRY')
  for r in analysis.bridges(rows):self.assertEqual(r['status'],'UNAVAILABLE_GEOMETRY');self.assertNotIn('total_ratio',r)
 def test_no_double_count_of_routing_hierarchy(self):
  for r in analysis.load():
   if r['status']!='FINISHED':continue
   for op in ('read','write'):
    total=D(r[op+'_bank_sum_pj']);self.assertEqual(total,D(r[op+'_data_bank_pj'])+D(r[op+'_tag_bank_pj']))
    self.assertEqual(total,D(r[op+'_routing_pj'])+D(r[op+'_nonrouting_residual_pj']))
 def test_exact_bridge_identities_from_raw(self):
  for x in analysis.bridges(analysis.load(),True):
   total=F(x['total_ratio']);self.assertEqual(total,F(x['node_first'])*F(x['capacity_after_node']));self.assertEqual(total,F(x['capacity_first'])*F(x['node_after_capacity']))
   self.assertTrue(x['identity_exact'])
 def test_fixed_capacity_sf_independently_from_raw(self):
  for row in analysis.fixed_sf(analysis.load()):
   values=[]
   kind='Hit' if row['operation']=='read' else 'Write'
   for key in ('from_log','to_log'):
    raw=(analysis.P/row[key]).read_text()
    values.append(D(re.search(r'Cache '+kind+r' Dynamic Energy\s*=\s*([\d.]+)nJ',raw).group(1))*1000)
   self.assertEqual(D(row['sf']),values[1]/values[0])
 def test_partition_dynamic_not_multiplied_by_N(self):
  rows=analysis.load();by={(r['node_nm'],r['capacity_mib'],r['objective']):r for r in rows}
  for x in analysis.partitions(rows):
   if x['status']!='VALID_LOCAL_CONTROL':continue
   local=by[x['node_nm'],8,x['objective']]
   self.assertEqual(D(x['read_local_pj_access']),D(local['read_summary_pj']))
   self.assertEqual(D(x['sum_local_leakage_mw']),4*D(local['leakage_mw']))
   self.assertIsNone(x['shared_fabric_energy_pj'])
 def test_uploaded_csv_precision_is_not_reused(self):
  audit=analysis.csv_precision_audit(analysis.load());self.assertEqual(len(audit),16)
  self.assertTrue(all(x['matches_mixed_at_4dp'] for x in audit))
  r=audit[0];self.assertNotEqual(D(r['uploaded_ratio']),D(r['consistent_bank_sum_ratio']))
 def test_real_resume_preserves_attempts(self):
  # Existing finished case must return before trying to launch a process.
  case=next(x for x in json.loads((R/'provenance/cases.json').read_text()) if x['group']=='fixed32')
  before=list((R/'logs'/case['run_id']).glob('*'))
  with patch.object(runner.subprocess,'Popen',side_effect=AssertionError('must not execute')),redirect_stdout(io.StringIO()):
   self.assertEqual(runner.run(case,1800)['status'],'FINISHED')
  self.assertEqual(before,list((R/'logs'/case['run_id']).glob('*')))
 def test_hash_corruption_rejected(self):
  row=next(x for x in analysis.load() if x['origin']=='new' and x['status']=='FINISHED')
  meta=analysis.P/row['metadata'];cfg=analysis.P/row['config'];cell=analysis.P/'NSCache_Experiment_DB/configs/New_Configs'/f"SRAM_cell_{row['node_nm']}nm.cell"
  with patch.object(analysis,'sha',return_value='bad'):
   with self.assertRaises(ValueError):analysis.read_raw(meta,cfg,cell,'new')
 def test_repeatable_analysis(self):
  def output():return {str(p):p.read_bytes() for p in (R/'results').glob('*') if p.is_file()}|{str(R/'reports/experiment_report.md'):(R/'reports/experiment_report.md').read_bytes()}
  with redirect_stdout(io.StringIO()):self.assertEqual(analysis.main(),0)
  first=output()
  with redirect_stdout(io.StringIO()):self.assertEqual(analysis.main(),0)
  self.assertEqual(first,output())
 def test_full_historical_hash_preservation(self):self.assertEqual(analysis.protected(),336)
if __name__=='__main__':unittest.main()
