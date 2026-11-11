"""Exercise raw-log regeneration, deterministic outputs and input rejection."""
from contextlib import redirect_stdout, redirect_stderr
from decimal import Decimal
import csv
import io
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import analyze
import snapshot_manifest


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'DB'
        source = Path(__file__).resolve().parents[1]
        for directory in ('configs', 'logs', 'results/recorded'):
            shutil.copytree(source / directory, self.root / directory)
        (self.root / 'reports').mkdir()
        self.patch = patch.object(analyze, 'ROOT', self.root)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        self.temp.cleanup()

    def run_analysis(self):
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            return analyze.main()

    def generated(self):
        return {str(p.relative_to(self.root)): p.read_bytes()
                for directory in ('results', 'reports') for p in (self.root / directory).rglob('*')
                if p.is_file()}

    def test_raw_regeneration_and_repeatability_without_binary_or_cached_results(self):
        # Deliberately bogus cached diagnostic values must never affect either matrix.
        (self.root / 'results/width_diagnostic.json').write_text('[{"read_pj_per_access": 999999}]')
        (self.root / 'reports').rmdir()  # Entire generated-report directory can be rebuilt.
        self.assertFalse((self.root / 'build/nsc').exists())
        self.assertEqual(self.run_analysis(), 1)  # Four documented historical discrepancies.
        before = self.generated()
        self.assertEqual(self.run_analysis(), 1)
        self.assertEqual(before, self.generated())
        trace = (self.root / 'reports/scaling_matrix_traceability.md').read_text()
        self.assertEqual(len(re.findall(r"id='(?:as|wa)-", trace)), 48)
        for name in ('scaling.csv', 'scaling_width_aligned.csv'):
            with (self.root / 'results' / name).open() as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(len(rows), 24)
            for row in rows:
                values = []
                for direction in ('from', 'to'):
                    raw = (self.root / row[direction + '_log']).read_text()
                    kind = 'Hit' if row['metric'].startswith('read') else 'Write'
                    match = re.search(r'Cache ' + kind + r' Dynamic Energy\s*=\s*([\d.]+)nJ', raw)
                    values.append(Decimal(match.group(1)) * 1000)
                self.assertEqual(Decimal(row['scaling_factor']), values[1] / values[0])
        self.assertIn('Width-Aligned Scaling Matrix', (self.root / 'reports/process_scaling_analysis.md').read_text())

    def test_corrupt_diagnostic_log_rejected_before_outputs_change(self):
        self.assertEqual(self.run_analysis(), 1)
        before = self.generated()
        log = next((self.root / 'logs/diagnostic_512bit').glob('*/*/stdout.log'))
        log.write_text(log.read_text().replace('Finished!', 'truncated'))
        self.assertEqual(self.run_analysis(), 2)
        self.assertEqual(before, self.generated())

    def test_changed_configuration_rejected(self):
        config = self.root / 'configs/study_reconstructed/L1_14nm.cfg'
        config.write_text(config.read_text().replace('512', '256'))
        self.assertEqual(self.run_analysis(), 2)
        self.assertEqual(list((self.root / 'reports').iterdir()), [])

    def test_failed_latest_attempt_does_not_fall_back_to_old_success(self):
        latest = self.root / 'logs/new/L1_14nm/99999999T000000Z'
        latest.mkdir()
        (latest / 'metadata.json').write_text(json.dumps({'status': 'FAILED', 'returncode': 7}))
        self.assertEqual(self.run_analysis(), 2)


class ManifestTests(unittest.TestCase):
    def test_inventory_hashes_repeatability_and_tamper_detection(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            subprocess.run(['git', 'init', '-q', str(repo)], check=True)
            (repo / 'README.md').write_text('root readme')
            root = repo / 'DB'
            (root / 'provenance').mkdir(parents=True)
            (root / 'reports').mkdir()
            (root / 'report.md').write_text('report')
            subprocess.run(['git', '-C', str(repo), 'add', '.'], check=True)
            subprocess.run(['git', '-C', str(repo), '-c', 'user.name=Test', '-c', 'user.email=test@example.org',
                            'commit', '-qm', 'fixture'], check=True)
            snapshot_manifest.snapshot(root, base='HEAD')
            manifest = (root / 'provenance/artifact_SHA256SUMS.txt').read_bytes()
            inventory = (root / 'provenance/directory_inventory.txt').read_bytes()
            snapshot_manifest.snapshot(root, base='HEAD')
            self.assertEqual(manifest, (root / 'provenance/artifact_SHA256SUMS.txt').read_bytes())
            self.assertEqual(inventory, (root / 'provenance/directory_inventory.txt').read_bytes())
            snapshot_manifest.snapshot(root, check=True, base='HEAD')
            self.assertIn(b'../README.md', manifest)
            self.assertIn(b'provenance/artifact_SHA256SUMS.txt', inventory)
            (repo / 'README.md').write_text('changed')
            with self.assertRaises(ValueError):
                snapshot_manifest.snapshot(root, check=True, base='HEAD')


if __name__ == '__main__':
    unittest.main()
