"""Verify raw-derived width comparisons, deterministic regeneration and failure rejection."""
from contextlib import redirect_stdout,redirect_stderr
import csv
from decimal import Decimal as D
import importlib.util
import io
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]


def module(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file)
    obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj

analysis=module('phase2_analysis','analyze.py')
prepare=module('phase2_prepare','prepare.py')
manifest=module('phase2_manifest','manifest.py')


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.repo=Path(self.temp.name)
        self.root=self.repo/'NSCache_Phase2A';self.p1=self.repo/'NSCache_Experiment_DB'
        for name in ('configs','logs','provenance'):
            shutil.copytree(ROOT/name,self.root/name)
        shutil.copytree(ROOT.parent/'NSCache_Experiment_DB',self.p1,ignore=shutil.ignore_patterns('build','runtime','__pycache__'))
        self.a=patch.object(analysis,'ROOT',self.root);self.b=patch.object(analysis,'P1',self.p1)
        self.a.start();self.b.start()

    def tearDown(self):self.b.stop();self.a.stop();self.temp.cleanup()

    def run_analysis(self):
        with redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):return analysis.main()

    def generated(self):
        return {str(p.relative_to(self.root)):p.read_bytes() for d in ('results','reports') for p in (self.root/d).rglob('*') if p.is_file()}

    def test_regeneration_from_raw_and_repeatability(self):
        # Cached Phase 1 comparison numbers must not be consulted.
        (self.p1/'results/scaling_width_aligned.csv').write_text('corrupted cached analysis')
        self.assertEqual(self.run_analysis(),0);first=self.generated()
        self.assertEqual(self.run_analysis(),0);self.assertEqual(first,self.generated())
        for name,count in [('phase2_256bit_energy.csv',16),('phase2_256bit_scaling.csv',24),('width_256_vs_512_comparison.csv',16),('width_256_vs_512_scaling.csv',24)]:
            with (self.root/'results'/name).open() as stream:rows=list(csv.DictReader(stream))
            self.assertEqual(len(rows),count)
            for row in rows:
                if name=='phase2_256bit_scaling.csv':
                    vals=[]
                    for key in ('from_log','to_log'):
                        kind='Hit' if row['metric'].startswith('read') else 'Write'
                        raw=(self.root/row[key]).read_text()
                        vals.append(D(re.search(r'Cache '+kind+r' Dynamic Energy\s*=\s*([\d.]+)nJ',raw).group(1))*1000)
                    self.assertEqual(D(row['scaling_factor']),vals[1]/vals[0])
                if name=='width_256_vs_512_comparison.csv':
                    for k in ('read','write'):
                        a,b=D(row[k+'_256_pj_access']),D(row[k+'_512_pj_access'])
                        self.assertEqual(D(row[k+'_E256_div_E512']),a/b)
                        self.assertEqual(D(row[k+'_256_effective_pj_bit']),a/256)
                        self.assertEqual(D(row[k+'_512_effective_pj_bit']),b/512)

    def test_raw_log_corruption_is_rejected_without_outputs(self):
        log=next((self.root/'logs/phase2_256bit').glob('*/*/stdout.log'));log.write_text('corrupt')
        self.assertEqual(self.run_analysis(),2)
        self.assertFalse((self.root/'results/phase2_256bit_energy.csv').exists())

    def test_configuration_change_beyond_width_is_rejected(self):
        config=self.root/'configs/phase2_256bit/L1_14nm.cfg'
        config.write_text(config.read_text().replace('300','301'))
        self.assertEqual(self.run_analysis(),2)

    def test_breakdown_does_not_add_nested_subarray_values(self):
        self.assertEqual(self.run_analysis(),0)
        with (self.root/'results/breakdown_width_comparison.csv').open() as f:rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),32)
        for r in rows:
            for w in (256,512):
                total=D(r[f'bank_total_{w}_pj']);route=D(r[f'routing_{w}_pj'])
                self.assertEqual(total,D(r[f'data_bank_{w}_pj'])+D(r[f'tag_bank_{w}_pj']))
                self.assertEqual(D(r[f'nonrouting_residual_{w}_pj']),total-route)
                self.assertLessEqual(route,total)


class PreservationTests(unittest.TestCase):
    def test_prepare_copies_only_width_and_preserves_unexpected_file(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'NSCache_Phase2A';(root/'configs/phase2_256bit').mkdir(parents=True);(root/'provenance').mkdir()
            p1=Path(d)/'NSCache_Experiment_DB'
            shutil.copytree(ROOT.parent/'NSCache_Experiment_DB/configs',p1/'configs')
            with patch.object(prepare,'ROOT',root),patch.object(prepare,'P1',p1),redirect_stdout(io.StringIO()):
                prepare.prepare()
                configs=list((root/'configs/phase2_256bit').glob('*.cfg'));self.assertEqual(len(configs),16)
                for c in configs:self.assertIn(b'-WordWidth (bit): 256',c.read_bytes())
                c=configs[0];c.write_text('user file')
                with self.assertRaises(ValueError):prepare.prepare()
                self.assertEqual(c.read_text(),'user file')

    def test_baseline_preservation_manifest(self):
        self.assertEqual(manifest.preserve(),226)

    def test_manifest_inventory_covers_all_tracked_phase2_files(self):
        names=subprocess.check_output(['git','-C',str(ROOT.parent),'ls-files','NSCache_Phase2A'],text=True).splitlines()
        tracked={str(Path(n).relative_to('NSCache_Phase2A')) for n in names}
        inventory=set((ROOT/'provenance/file_inventory.txt').read_text().splitlines())
        self.assertEqual(inventory,tracked)
        self.assertIn('logs/build/stdout.log',inventory)


if __name__=='__main__':unittest.main()
