from pathlib import Path
import subprocess, unittest
ROOT=Path(__file__).resolve().parents[1]
DOMAINS=('robotics-production','software-development','specialty-care-administration','soc-operations','logistics-supply-chain')
class OrganizationalSimulationTests(unittest.TestCase):
    def test_wrappers_are_thin_and_complete(self):
        common=(ROOT/'organizational-simulations/run.sh').read_text()
        self.assertIn('AXIOM_RESEARCH_DIR',common); self.assertIn('/tmp/axiom-demo-$domain',common)
        self.assertNotIn('write_file',common); self.assertNotIn('ASON',common)
        for d in DOMAINS:
            p=ROOT/'organizational-simulations'/f'{d}.sh'; self.assertTrue(p.is_file()); self.assertIn(f'run.sh" "{d}"',p.read_text())
    def test_unknown_domain_fails_without_execution(self):
        cp=subprocess.run([str(ROOT/'organizational-simulations/run.sh'),'unknown'],capture_output=True,text=True)
        self.assertEqual(cp.returncode,2); self.assertIn('unsupported simulation',cp.stderr)
if __name__=='__main__': unittest.main()
