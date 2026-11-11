"""Validate built artifacts and smoke-check the same bytes after deployment."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
import tempfile
import threading
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validate_site import validate_site
from smoke_site import smoke
from run_validation import require_fresh_output


class ArtifactChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'index.html').write_text('<html><a href="/works/piece/">Piece</a><script src="/js/catalog.js"></script></html>')
        (self.root / 'works/piece').mkdir(parents=True)
        (self.root / 'works/piece/index.html').write_text('<html>Piece</html>')
        (self.root / 'js').mkdir()
        (self.root / 'js/catalog.js').write_text('console.log("catalog")')

    def test_valid_routes_and_local_assets(self):
        self.assertEqual(validate_site(self.root, 'https://example.org/'), [])

    def test_empty_or_missing_artifact_cannot_pass(self):
        self.assertTrue(validate_site(self.root / 'missing', 'https://example.org/'))

    def test_stale_build_output_is_rejected_without_deleting_it(self):
        with self.assertRaises(ValueError):
            require_fresh_output(self.root)
        self.assertTrue((self.root / 'index.html').is_file())
        require_fresh_output(self.root / 'fresh')

    def test_missing_local_asset_and_route_fail(self):
        (self.root / 'index.html').write_text('<img src="/media/missing.jpg"><a href="/works/missing/">Missing</a>')
        errors = '\n'.join(validate_site(self.root, 'https://example.org/'))
        self.assertIn('media/missing.jpg', errors)
        self.assertIn('works/missing', errors)

    def test_subdirectory_base_url_resolves_correctly(self):
        (self.root / 'index.html').write_text('<script src="/SaxoBrain/js/catalog.js"></script>')
        self.assertEqual(validate_site(self.root, 'https://example.org/SaxoBrain/'), [])

    def test_host_root_link_cannot_masquerade_as_a_project_asset(self):
        self.assertIn('outside the hosting prefix', '\n'.join(validate_site(self.root, 'https://example.org/SaxoBrain/')))

    def test_vault_and_private_research_leaks_fail(self):
        (self.root / 'index.html').write_text('<p>![[Catalog.base]]</p><h2 id="research-notes-private">Research notes (private)</h2>')
        errors = '\n'.join(validate_site(self.root, 'https://example.org/'))
        self.assertIn('vault', errors)
        self.assertIn('private', errors)

    def test_project_reference_output_fails(self):
        (self.root / 'project-reference').mkdir()
        (self.root / 'project-reference/private.html').write_text('private')
        self.assertTrue(validate_site(self.root, 'https://example.org/'))

    def test_smoke_requires_revision_and_exact_artifact_bytes(self):
        (self.root / 'release.json').write_text('{"revision":"' + 'a' * 40 + '"}')
        class Quiet(SimpleHTTPRequestHandler):
            def log_message(self, *args):
                pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(self.root)))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        url = f'http://127.0.0.1:{server.server_port}/'
        self.assertEqual(smoke(url, self.root, 'a' * 40, ['index.html', 'js/catalog.js']), [])
        self.assertTrue(smoke(url, self.root, 'b' * 40, ['index.html']))
        self.assertTrue(smoke(url, self.root, 'a' * 40, ['missing.html']))


if __name__ == '__main__':
    unittest.main()
