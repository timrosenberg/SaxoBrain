"""Verify YouTube queues through the real work-page renderer."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from urllib.parse import parse_qs, urlparse

from test_content_authoring import Document, ROOT


class StreamingQueue(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        root = Path(cls.tmp.name)
        shutil.copy(ROOT / 'hugo.toml', root / 'hugo.toml')
        shutil.copytree(ROOT / 'content/Site Text', root / 'content/Site Text')
        (root / 'content/works').mkdir()
        cls.queue = ('https://www.youtube.com/watch_videos?video_ids='
                     'canzmfkKXTE,ey2_4S_Yu2k,g07NP5650u8,aqK3fh7al08,fUkAP6YTh4A')
        for slug, url in [('queue', cls.queue),
                          ('single', 'https://youtu.be/canzmfkKXTE?t=42')]:
            (root / f'content/works/{slug}.md').write_text(
                f'---\ntitle: {slug}\nslug: {slug}\ninstruments: [Alto Saxophone]\n'
                f'streaming: {url}\n---\n')
        result = subprocess.run(
            ['hugo', '--source', str(root), '--layoutDir', str(ROOT / 'layouts')],
            text=True, capture_output=True)
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)
        cls.docs = {slug: Document((root / f'public/works/{slug}/index.html').read_text())
                    for slug in ['queue', 'single']}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_queue_embeds_all_five_videos_in_supplied_order(self):
        frames = [attrs for tag, attrs in self.docs['queue'].tags if tag == 'iframe']
        self.assertEqual(len(frames), 1)
        src = urlparse(frames[0]['src'])
        self.assertEqual(src.netloc, 'www.youtube-nocookie.com')
        self.assertEqual(src.path, '/embed/canzmfkKXTE')
        self.assertEqual(parse_qs(src.query)['playlist'],
                         ['canzmfkKXTE,ey2_4S_Yu2k,g07NP5650u8,aqK3fh7al08,fUkAP6YTh4A'])
        self.assertTrue(any(tag == 'a' and attrs.get('href') == self.queue
                            for tag, attrs in self.docs['queue'].tags))

    def test_individual_video_keeps_its_start_time(self):
        frames = [attrs for tag, attrs in self.docs['single'].tags if tag == 'iframe']
        self.assertEqual(len(frames), 1)
        self.assertEqual(frames[0]['src'],
                         'https://www.youtube-nocookie.com/embed/canzmfkKXTE?start=42')


if __name__ == '__main__':
    unittest.main()
