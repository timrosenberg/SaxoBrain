"""Content contracts tested against small editable vaults."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validate_content import validate


class ContentValidation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.write('content/composers/Composer.md', 'title: Composer\nslug: composer')
        self.work = 'title: Piece\nslug: piece\ncomposer: ["[[Composer]]"]\ninstruments: [Alto Saxophone]'
        self.write('content/works/Piece.md', self.work)

    def write(self, path, fields, body=''):
        p = self.root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('---\n' + fields + '\n---\n' + body)

    def check(self, extra, expected):
        self.write('content/works/Piece.md', self.work + '\n' + extra)
        self.assertIn(expected, '\n'.join(validate(self.root)))

    def test_unknown_optional_fields_are_valid(self):
        self.write('content/works/Piece.md', self.work + '\ncomposed:\nyear-of-study:\nstreaming:\npurchase: []')
        self.assertEqual(validate(self.root), [])

    def test_year_is_number_and_never_boolean(self):
        for value in ['"2020"', 'true', '[2020]']:
            with self.subTest(value=value):
                self.check('composed: ' + value, 'composed: expected an integer')

    def test_required_fields_and_list_shape(self):
        self.write('content/works/Piece.md', 'title: Piece\nslug: piece\ncomposer: Composer')
        errors = '\n'.join(validate(self.root))
        self.assertIn('composer: expected a nonempty list', errors)
        self.assertIn('instruments: expected a nonempty list', errors)

    def test_yaml_parse_error_names_the_note(self):
        self.check('purchase: [broken', 'content/works/Piece.md: YAML')

    def test_duplicate_yaml_key_is_rejected(self):
        self.check('slug: duplicate', 'duplicate key: slug')

    def test_missing_composer_is_rejected(self):
        self.write('content/works/Piece.md', self.work.replace('[[Composer]]', '[[Typo]]'))
        self.assertIn('composer: unresolved composer [[Typo]]', '\n'.join(validate(self.root)))

    def test_unknown_study_level_is_rejected_without_assigning_one(self):
        self.check('year-of-study: Expert', 'year-of-study: unrecognized value')

    def test_existing_precollege_and_private_photo_provenance_are_valid(self):
        self.write('content/works/Piece.md', self.work + '\nyear-of-study: Pre-college')
        self.write('content/composers/Composer.md', 'title: Composer\nslug: composer\nphoto-source: Notion upload')
        self.assertEqual(validate(self.root), [])

    def test_collection_can_have_no_single_composer(self):
        self.write('content/works/Piece.md', self.work.replace('["[[Composer]]"]', '[]'))
        self.assertEqual(validate(self.root), [])

    def test_streaming_scalar_and_labeled_list_are_supported(self):
        for text in ['https://youtu.be/abcdefghijk', '["Movement I · https://example.org/audio.mp3"]']:
            self.write('content/works/Piece.md', self.work + '\nstreaming: ' + text)
            self.assertEqual(validate(self.root), [])

    def test_unsafe_and_malformed_links_are_rejected(self):
        for text in ['javascript:alert(1)', 'https://', '//example.org/track', 'https://example.org/bad link']:
            with self.subTest(text=text):
                self.check('streaming: "' + text + '"', 'streaming: invalid link')

    def test_mailto_purchase_is_valid(self):
        self.write('content/works/Piece.md', self.work + '\npurchase: [mailto:composer@example.org]')
        self.assertEqual(validate(self.root), [])

    def test_missing_local_media_is_rejected(self):
        self.check('download: [/media/missing.pdf]', 'download: missing local asset')

    def test_site_text_preserves_placeholders_against_baseline(self):
        self.write('content/Site Text/Pieces.md', 'title: Pieces', '| Setting | Text |\n| --- | --- |\n| piece-recording-of | Recording |\n')
        baseline = self.root / 'previous'
        p = baseline / 'content/Site Text/Pieces.md'
        p.parent.mkdir(parents=True)
        p.write_text('---\ntitle: Pieces\n---\n| Setting | Text |\n| --- | --- |\n| piece-recording-of | Recording of {title} |\n')
        self.assertIn('piece-recording-of: placeholders changed', '\n'.join(validate(self.root, baseline)))

    def test_duplicate_page_names_are_rejected(self):
        self.write('content/reading/Composer.md', 'title: Other\nslug: other')
        self.assertIn('ambiguous page name', '\n'.join(validate(self.root)))

    def test_new_frontmatter_contract_is_structural(self):
        self.check('layout: malicious', 'layout: unsupported property')

    def test_hidden_optional_dates_and_numeric_duration_remain_valid(self):
        self.write('content/works/Piece.md', self.work + '\nadded: 2026-11-11\nduration: 8\nresearch: []\nwant-to-play: false')
        self.assertEqual(validate(self.root), [])


if __name__ == '__main__':
    unittest.main()
