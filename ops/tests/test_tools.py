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
 def test_bundle_treats_shell_metacharacters_as_literal_filenames(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); name='payload$(touch INJECTED).txt'; (root/name).write_text('literal content\\n')
   result=subprocess.run(["bash",str(ROOT/"files/bundle-text.sh")],cwd=root,text=True,capture_output=True)
   self.assertFalse((root/"INJECTED").exists(),"filename executed shell code")
   self.assertEqual(result.returncode,0,result.stderr)
   self.assertIn(name,(root/"combined.txt").read_text())
   self.assertIn("literal content",(root/"combined.txt").read_text())

 def test_split_rejects_paths_outside_output_directory(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); out=root/"out"; out.mkdir()
   for name in ["../escape.txt",str(root/"absolute.txt")]:
    src=root/"bundle.txt"; src.write_text(f"===== BEGIN FILE: {name} =====\npayload\n===== END FILE: {name} =====\n")
    result=subprocess.run(["python",str(ROOT/"files/split_text_bundle.py"),str(src),str(out)],capture_output=True,text=True)
    self.assertNotEqual(result.returncode,0)
    self.assertFalse((root/"escape.txt").exists())
    self.assertFalse((root/"absolute.txt").exists())

if __name__=="__main__": unittest.main()
