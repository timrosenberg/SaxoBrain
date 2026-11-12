"""Exercise body-authored YouTube playlists through real Hugo rendering."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from test_content_authoring import Document, ROOT


class BodyYouTubePlaylists(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        root = Path(cls.tmp.name)
        shutil.copy(ROOT / 'hugo.toml', root / 'hugo.toml')
        shutil.copytree(ROOT / 'content/Site Text', root / 'content/Site Text')
        (root / 'content/recordings').mkdir()
        body = '\n\n'.join(
            f'## Volume {i}\n\n'
            f'[https://www.youtube.com/playlist?list=PLvolume{i}]'
            f'(https://www.youtube.com/playlist?list=PLvolume{i} "Volume {i}")'
            for i in range(2, 9))
        (root / 'content/recordings/series.md').write_text(
            '---\ntitle: Series\nslug: series\nembed-youtube: true\n'
            'youtube: https://www.youtube.com/playlist?list=PLvolume1\n'
            'tracks: ["First movement · 1:23"]\n---\n'
            '> [!caption]\n> ## Volume 1\n\n' + body)
        playlist = 'https://www.youtube.com/playlist?list=PLordinary'
        for name, flag, content in [
            ('opt-out', False, f'<{playlist}>'),
            ('labeled', True, f'[Listen to this album]({playlist})'),
            ('single', True, '<https://youtu.be/canzmfkKXTE?t=42>'),
            ('fallback-title', True, '<https://music.youtube.com/playlist?hl=en&list=PLfallback>'),
            ('invalid-host', True, '<https://www.youtube.com.example.org/playlist?list=PLbad>'),
            ('empty-list', True, '<https://www.youtube.com/playlist?list=>'),
        ]:
            (root / f'content/{name}.md').write_text(
                f'---\ntitle: {name}\nembed-youtube: {str(flag).lower()}\n---\n{content}\n')
        result = subprocess.run(
            ['hugo', '--source', str(root), '--layoutDir', str(ROOT / 'layouts')],
            text=True, capture_output=True)
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)
        cls.html = (root / 'public/recordings/series/index.html').read_text()
        cls.docs = {'series': Document(cls.html)}
        for name in ['opt-out', 'labeled', 'single', 'fallback-title', 'invalid-host', 'empty-list']:
            cls.docs[name] = Document((root / f'public/{name}/index.html').read_text())

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def frames(self, name):
        return [attrs for tag, attrs in self.docs[name].tags if tag == 'iframe']

    def test_eight_volume_players_render_once_in_order(self):
        frames = self.frames('series')
        self.assertEqual([f['src'].split('&')[0] for f in frames], [
            f'https://www.youtube-nocookie.com/embed/videoseries?list=PLvolume{i}'
            for i in range(1, 9)])
        for i in range(1, 9):
            self.assertIn(f'>Volume {i}</h2>', self.html)

    def test_playlist_players_are_lazy_accessible_and_fullscreen(self):
        frames = self.frames('series')
        self.assertEqual(len(frames), 8)
        for i, frame in enumerate(frames[1:], 2):
            self.assertEqual(frame['title'], f'Volume {i}')
            self.assertEqual(frame['loading'], 'lazy')
            self.assertIn('allowfullscreen', frame)
            self.assertNotIn('autoplay=1', frame['src'])

    def test_first_volume_keeps_its_track_controls(self):
        controls = self.docs['series'].matching('button', 'track')
        self.assertEqual(len(controls), 1)
        self.assertEqual(controls[0]['data-i'], '0')
        self.assertIn('enablejsapi=1', self.frames('series')[0]['src'])

    def test_opt_out_custom_labels_and_invalid_urls_stay_links(self):
        for name in ['opt-out', 'labeled', 'invalid-host', 'empty-list']:
            with self.subTest(name=name):
                self.assertFalse(self.frames(name))
                self.assertTrue(any(tag == 'a' and 'playlist?' in attrs.get('href', '')
                                    for tag, attrs in self.docs[name].tags))

    def test_individual_video_retains_start_time(self):
        self.assertEqual(self.frames('single')[0]['src'],
                         'https://www.youtube-nocookie.com/embed/canzmfkKXTE?start=42')

    def test_playlist_with_other_query_parameters_gets_default_title(self):
        frames = self.frames('fallback-title')
        self.assertEqual(len(frames), 1)
        self.assertEqual(frames[0]['src'],
                         'https://www.youtube-nocookie.com/embed/videoseries?list=PLfallback')
        self.assertTrue(frames[0]['title'])


class BodyRecordingCallouts(unittest.TestCase):
    def test_spotify_album_players_reuse_existing_renderer(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copy(ROOT / 'hugo.toml', root / 'hugo.toml')
            shutil.copytree(ROOT / 'content/Site Text', root / 'content/Site Text')
            (root / 'content/players.md').write_text('''---
title: Players
---
## Volume 7

> [!recording] [Volume 7](https://open.spotify.com/album/7i8wGE3snEE0Sb6vf2ERVK)
>
> Optional body text remains visible.

## Volume 8

> [!recording] [Volume 8](https://open.spotify.com/album/3dgBGSW89q32jDG1T8syXX)

> [!recording] Without a link
>
> Retain this fallback.
''')
            result = subprocess.run(
                ['hugo', '--source', str(root), '--layoutDir', str(ROOT / 'layouts')],
                text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            html = (root / 'public/players/index.html').read_text()
            doc = Document(html)
            frames = [attrs for tag, attrs in doc.tags if tag == 'iframe']
            self.assertEqual([frame['src'] for frame in frames], [
                'https://open.spotify.com/embed/album/7i8wGE3snEE0Sb6vf2ERVK',
                'https://open.spotify.com/embed/album/3dgBGSW89q32jDG1T8syXX'])
            for i, frame in enumerate(frames, 7):
                self.assertIn(f'Volume {i}', frame['title'])
                self.assertEqual(frame['loading'], 'lazy')
            self.assertIn('Optional body text remains visible.', html)
            self.assertIn('Retain this fallback.', html)
            self.assertEqual(doc.max_anchor_depth, 1)


if __name__ == '__main__':
    unittest.main()
