import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHROMIUM = shutil.which("chromium") or shutil.which("chromium-browser")

HARNESS = r'''<script>
(async()=>{
  const enc=new TextEncoder(); let calls=0;
  const response=(text,status=200,delay=0)=>({ok:status>=200&&status<300,status,body:{getReader(){let sent=false;return{async read(){if(sent)return{done:true};sent=true;if(delay)await new Promise(r=>setTimeout(r,delay));return{done:false,value:enc.encode('data: '+JSON.stringify({candidates:[{content:{parts:[{text}]}}]})+'\n\n')}}}}}});
  window.fetch=async(url,opt)=>{calls++;const prompt=JSON.parse(opt.body).contents[0].parts[0].text;if(prompt.includes('Failure'))return response('',500);if(prompt.includes('Alpha')){await new Promise((resolve,reject)=>{const t=setTimeout(resolve,80);opt.signal.addEventListener('abort',()=>{clearTimeout(t);reject(new DOMException('Aborted','AbortError'))},{once:true})});return response('stale alpha')}if(prompt.includes('Gamma'))return response('Gamma delta.');return response('Beta gamma.');};
  try{
    gk.value='test-key';
    const a=InfiniteWiki.load('Alpha'); const b=InfiniteWiki.load('Beta'); await Promise.allSettled([a,b]);
    if(head.textContent!=='Beta'||content.textContent!=='Beta gamma.')throw Error('abort/stream');
    const link=content.querySelector('.w'); if(!link)throw Error('navigation link'); link.click(); await new Promise(r=>setTimeout(r,20));
    if(head.textContent!=='Beta')throw Error('first token navigation');
    await InfiniteWiki.load('Gamma'); if(!content.textContent.includes('Gamma delta.'))throw Error('stream');
    await InfiniteWiki.load('Failure'); if(!content.textContent.includes('HTTP 500'))throw Error('http error');
    document.body.dataset.testResult='pass'; document.body.dataset.calls=String(calls);
  }catch(e){document.body.dataset.testResult='fail:'+e.message}
})();
</script>'''

class BrowserTest(unittest.TestCase):
    @unittest.skipUnless(CHROMIUM, "Chromium not installed")
    def test_stream_abort_navigation_and_error(self):
        source=(ROOT/'index.html').read_text(encoding='utf-8')
        self.assertIn("x-goog-api-key", source)
        self.assertNotIn("localStorage", source)
        self.assertNotIn("Typecast", source)
        with tempfile.TemporaryDirectory() as tmp:
            page=Path(tmp)/'index.html'
            page.write_text(source.replace('</body>', HARNESS+'\n</body>'), encoding='utf-8')
            result=subprocess.run([CHROMIUM,'--headless=new','--no-sandbox','--disable-gpu','--disable-dev-shm-usage','--no-zygote','--virtual-time-budget=3000','--timeout=10000','--dump-dom',page.as_uri()],capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('data-test-result="pass"',result.stdout)

if __name__=='__main__':
    unittest.main()
