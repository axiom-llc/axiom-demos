import subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class MigratedTools(unittest.TestCase):
 def test_shell_syntax(self):
  ps=[ROOT/"files/bundle-text.sh",ROOT/"media/extract-frames.sh",ROOT/"media/check-metadata.sh"]
  for p in ps: self.assertTrue(p.is_file(),str(p))
  for p in ps: subprocess.run(["bash","-n",str(p)],check=True)
 def test_json_to_md(self):
  with tempfile.TemporaryDirectory() as td:
   src=Path(td)/"x.json"; src.write_text('{"a":1}')
   p=subprocess.run(["python",str(ROOT/"converters/json_to_md.py"),str(src)],text=True,capture_output=True,check=True)
   self.assertIn("a",p.stdout); self.assertIn("1",p.stdout)
 def test_bundle_split_content(self):
  with tempfile.TemporaryDirectory() as td:
   t=Path(td); (t/"a.txt").write_text("alpha\n"); (t/"b.txt").write_text("beta\n")
   subprocess.run(["bash",str(ROOT/"files/bundle-text.sh")],cwd=t,check=True)
   out=t/"out"; out.mkdir(); subprocess.run(["python",str(ROOT/"files/split_text_bundle.py"),str(t/"combined.txt"),str(out)],check=True)
   self.assertEqual((out/"a.txt").read_text().strip(),"alpha"); self.assertEqual((out/"b.txt").read_text().strip(),"beta")

if __name__=="__main__": unittest.main()
