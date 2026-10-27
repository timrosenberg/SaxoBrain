"""Verify recording players through the real work-page renderer."""
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
                          ('single', 'https://youtu.be/canzmfkKXTE?t=42'),
                          ('spotify', 'https://open.spotify.com/track/0Ld77xxSxrrnuj1HBkqYl9'),
                          ('apple', 'https://music.apple.com/us/album/123?i=456'),
                          ('soundcloud', 'https://soundcloud.com/performer/recording'),
                          ('single-audio', 'https://example.com/recording.MP3?version=2'),
                          ('external', 'https://example.com/listen?file=recording.mp3')]:
            (root / f'content/works/{slug}.md').write_text(
                f'---\ntitle: {slug}\nslug: {slug}\ninstruments: [Alto Saxophone]\n'
                f'streaming: {url}\n---\n')
        (root / 'content/works/audio.md').write_text(
            '---\ntitle: Audio\nslug: audio\ninstruments: [Soprano Saxophone]\n'
            'streaming:\n'
            '  - "I. The Horizon Beckons · https://garrop.com/resources/Slipstream-DSO-Mvmt-1.mp3"\n'
            '  - "II. Riding Solo · https://garrop.com/resources/Slipstream-DSO-mvmt-2.mp3"\n'
            '  - "III. Adrenaline Rush · https://garrop.com/resources/Slipstream-DSO-mvmt-3.mp3"\n'
            '---\n')
        (root / 'content/works/mixed.md').write_text(
            '---\ntitle: Mixed\nslug: mixed\ninstruments: [Alto Saxophone]\n'
            'streaming:\n'
            '  - "Source archive · https://example.com/archive"\n'
            '  - "Performance · https://youtu.be/canzmfkKXTE?t=42"\n'
            '---\n')
        result = subprocess.run(
            ['hugo', '--source', str(root), '--layoutDir', str(ROOT / 'layouts')],
            text=True, capture_output=True)
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)
        cls.docs = {slug: Document((root / f'public/works/{slug}/index.html').read_text())
                    for slug in ['queue', 'single', 'audio', 'single-audio', 'external',
                                 'spotify', 'apple', 'soundcloud', 'mixed']}

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
        self.assertFalse(self.docs['queue'].matching('a', 'recording-link'))

    def test_individual_video_keeps_its_start_time(self):
        frames = [attrs for tag, attrs in self.docs['single'].tags if tag == 'iframe']
        self.assertEqual(len(frames), 1)
        self.assertEqual(frames[0]['src'],
                         'https://www.youtube-nocookie.com/embed/canzmfkKXTE?start=42')

    def test_mp3_movements_play_inline_with_labels_and_without_autoloading(self):
        players = [attrs for tag, attrs in self.docs['audio'].tags if tag == 'audio']
        self.assertEqual([p['src'] for p in players], [
            'https://garrop.com/resources/Slipstream-DSO-Mvmt-1.mp3',
            'https://garrop.com/resources/Slipstream-DSO-mvmt-2.mp3',
            'https://garrop.com/resources/Slipstream-DSO-mvmt-3.mp3'])
        self.assertEqual([p['aria-label'] for p in players],
                         ['I. The Horizon Beckons', 'II. Riding Solo', 'III. Adrenaline Rush'])
        for player in players:
            self.assertIn('controls', player)
            self.assertEqual(player.get('preload'), 'none')
            self.assertNotIn('autoplay', player)

    def test_single_mp3_listen_button_stays_on_the_work_page(self):
        doc = self.docs['single-audio']
        listen = [attrs for tag, attrs in doc.tags
                  if tag == 'a' and 'primary' in attrs.get('class', '').split()]
        self.assertEqual(listen[0]['href'], '/works/single-audio/#streaming-recordings')
        players = [attrs for tag, attrs in doc.tags if tag == 'audio']
        self.assertEqual(players[0]['src'], 'https://example.com/recording.MP3?version=2')

    def test_webpage_with_mp3_in_query_remains_an_external_link(self):
        doc = self.docs['external']
        self.assertFalse(any(tag == 'audio' for tag, _ in doc.tags))
        self.assertEqual(doc.matching('a', 'recording-link')[0]['href'],
                         'https://example.com/listen?file=recording.mp3')
        listen = [attrs for tag, attrs in doc.tags
                  if tag == 'a' and 'primary' in attrs.get('class', '').split()]
        self.assertEqual(listen[0]['href'], 'https://example.com/listen?file=recording.mp3')

    def test_listen_targets_inline_player_for_each_supported_service(self):
        for slug in ['queue', 'single', 'spotify', 'apple', 'soundcloud', 'mixed']:
            with self.subTest(slug=slug):
                doc = self.docs[slug]
                self.assertTrue(any(tag == 'iframe' for tag, _ in doc.tags))
                listen = [attrs for tag, attrs in doc.tags
                          if tag == 'a' and 'primary' in attrs.get('class', '').split()]
                self.assertEqual(listen[0]['href'], f'/works/{slug}/#streaming-recordings')
                fallback = doc.matching('a', 'recording-link')
                self.assertEqual([link['href'] for link in fallback],
                                 ['https://example.com/archive'] if slug == 'mixed' else [])


if __name__ == '__main__':
    unittest.main()
