"""Guard against unit errors, incomplete parsing, forged resume, and lost failures."""
from decimal import Decimal
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import analyze
import run_experiments as runner

class ParserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=(analyze.ROOT/'logs/bundled/L1_14nm.log').read_text()

    def test_units_and_separate_data_tag(self):
        values,org=analyze.parse(self.raw)
        self.assertEqual(values['read_pj_per_access'],Decimal('74'))
        self.assertEqual(values['write_pj_per_access'],Decimal('58'))
        self.assertEqual(values['leakage_mw'],Decimal('.031'))
        self.assertEqual(org['data']['mat'],'256 Rows x 64 Columns')
        self.assertEqual(org['tag']['mat'],'8 Rows x 40 Columns')

    def test_missing_summary_rejected(self):
        with self.assertRaises(ValueError):
            analyze.parse(self.raw.replace('Cache Hit Dynamic Energy','missing'))

    def test_duplicate_summary_rejected(self):
        with self.assertRaises(ValueError):
            analyze.parse(self.raw+'\n - Cache Hit Latency = 0.434ns\n')

    def test_missing_tag_rejected(self):
        with self.assertRaises(ValueError):
            analyze.parse(self.raw.replace('CONFIGURATION','MISSING',1))

class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        for d in ('build','configs/study_reconstructed','configs/New_Configs','logs/build'):
            (self.root/d).mkdir(parents=True)
        (self.root/'build/nsc').write_text('binary fixture')
        (self.root/'configs/New_Configs/SRAM_cell_14nm.cell').write_text('cell fixture')
        (self.root/'logs/build/environment.json').write_text('{}')
        self.cfg=self.root/'configs/study_reconstructed/L1_14nm.cfg'
        self.cfg.write_text('config fixture')
        self.patch=patch.object(runner,'ROOT',self.root);self.patch.start()

    def tearDown(self):
        self.patch.stop();self.temp.cleanup()

    def finished(self,*args,**kwargs):
        kwargs['stdout'].write(b'Finished!\n');return subprocess.CompletedProcess(args,0)

    def test_resume_requires_log_integrity(self):
        with patch.object(runner.subprocess,'run',side_effect=self.finished) as call:
            runner.run(self.cfg,5)
            runner.run(self.cfg,5)
            self.assertEqual(call.call_count,1)
            next((self.root/'logs/new').glob('*/*/stdout.log')).write_text('tampered')
            runner.run(self.cfg,5)
            self.assertEqual(call.call_count,2)

    def test_changed_cell_requires_rerun(self):
        with patch.object(runner.subprocess,'run',side_effect=self.finished) as call:
            runner.run(self.cfg,5)
            (self.root/'configs/New_Configs/SRAM_cell_14nm.cell').write_text('changed')
            runner.run(self.cfg,5)
            self.assertEqual(call.call_count,2)

    def test_failure_preserved_then_retried(self):
        with patch.object(runner.subprocess,'run',return_value=subprocess.CompletedProcess([],7)):
            self.assertEqual(runner.run(self.cfg,5)['status'],'FAILED')
        with patch.object(runner.subprocess,'run',side_effect=self.finished):
            self.assertEqual(runner.run(self.cfg,5)['status'],'FINISHED')
        attempts=list((self.root/'logs/new').glob('*/*/metadata.json'))
        self.assertEqual(len(attempts),2)
        self.assertEqual({json.loads(p.read_text())['status'] for p in attempts},{'FAILED','FINISHED'})

    def test_timeout_preserved(self):
        with patch.object(runner.subprocess,'run',side_effect=subprocess.TimeoutExpired('fixture',5)):
            meta=runner.run(self.cfg,5)
        self.assertEqual(meta['status'],'TIMEOUT')
        self.assertIsNone(meta['returncode'])
        self.assertIn('stdout_sha256',meta)

if __name__=='__main__': unittest.main()
