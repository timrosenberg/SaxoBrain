"""Exercise real Git history and fake GitHub records without production writes."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from publishing_policy import structural_changes, verify_history, review_errors, healthy_baseline


class PublishingPolicy(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.git('init', '-q', '-b', 'main')
        self.git('config', 'user.name', 'Test')
        self.git('config', 'user.email', 'test@example.org')
        self.put('content/works/Piece.md', '---\ntitle: Piece\nslug: piece\ncomposer: []\ninstruments: [Alto Saxophone]\n---\n')
        self.base = self.commit()

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args], text=True).strip()

    def put(self, path, text):
        p = self.root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)

    def commit(self):
        self.git('add', '.')
        self.git('commit', '-qm', 'test')
        return self.git('rev-parse', 'HEAD')

    def test_work_and_media_updates_are_content(self):
        self.put('content/works/Piece.md', '---\ntitle: Corrected\nslug: piece\ncomposer: []\ninstruments: [Alto Saxophone]\nstreaming: https://youtu.be/abcdefghijk\n---\nUseful prose\n')
        self.put('static/media/works/piece/cover.jpg', 'image')
        self.assertEqual(structural_changes(self.root, self.base, self.commit()), [])

    def test_unknown_metadata_and_build_controls_are_structural(self):
        for field in ['layout', 'outputs', 'cascade', 'new-field']:
            with self.subTest(field=field):
                self.put('content/works/Piece.md', '---\ntitle: Piece\nslug: piece\n' + field + ': changed\n---\n')
                self.assertIn('content/works/Piece.md', structural_changes(self.root, self.base, self.commit()))

    def test_workflow_or_javascript_cannot_use_content_path(self):
        self.put('.github/workflows/publish.yml', 'jobs: {}')
        self.put('static/js/catalog.js', 'broken')
        changed = structural_changes(self.root, self.base, self.commit())
        self.assertIn('.github/workflows/publish.yml', changed)
        self.assertIn('static/js/catalog.js', changed)

    def test_adding_or_removing_site_text_keys_is_structural(self):
        self.put('content/Site Text/Pieces.md', '---\ntitle: Pieces\n---\n| Setting | Text |\n| --- | --- |\n| key | Copy {title} |\n')
        start = self.commit()
        self.put('content/Site Text/Pieces.md', '---\ntitle: Pieces\n---\n| Setting | Text |\n| --- | --- |\n| new-key | Copy {title} |\n')
        self.assertTrue(structural_changes(self.root, start, self.commit()))

    def test_content_push_cannot_hide_an_earlier_structural_commit(self):
        self.put('layouts/page.html', 'changed')
        structural = self.commit()
        self.put('content/works/New.md', '---\ntitle: New\nslug: new\ncomposer: []\ninstruments: [Alto Saxophone]\n---\n')
        head = self.commit()
        checked = []
        def review(sha):
            checked.append(sha)
            return ['no reviewed PR']
        self.assertIn('no reviewed PR', '\n'.join(verify_history(self.root, self.base, head, review)))
        self.assertEqual(checked, [structural])

    def test_reverting_a_structural_change_does_not_erase_its_history(self):
        self.put('layouts/page.html', 'changed')
        self.commit()
        self.git('revert', '--no-edit', 'HEAD')
        self.assertTrue(verify_history(self.root, self.base, self.git('rev-parse', 'HEAD'), lambda sha: ['unreviewed']))

    def test_reviewed_structure_followed_by_content_is_allowed(self):
        self.put('layouts/page.html', 'changed')
        self.commit()
        self.assertEqual(verify_history(self.root, self.base, self.git('rev-parse', 'HEAD'), lambda sha: []), [])

    def test_invalid_content_syntax_can_be_corrected_directly(self):
        original = (self.root / 'content/works/Piece.md').read_text()
        self.put('content/works/Piece.md', original.replace('composer: []', 'composer: [broken'))
        self.commit()
        self.put('content/works/Piece.md', original.replace('title: Piece', 'title: Corrected piece'))
        head = self.commit()
        self.assertEqual(verify_history(self.root, self.base, head, lambda sha: ['no PR']), [])

    def test_invalid_content_cannot_hide_a_new_rendering_contract(self):
        original = (self.root / 'content/works/Piece.md').read_text()
        self.put('content/works/Piece.md', original.replace('composer: []', 'composer: [broken'))
        self.commit()
        self.put('content/works/Piece.md', original.replace('slug: piece', 'slug: piece\nlayout: custom'))
        head = self.commit()
        self.assertTrue(verify_history(self.root, self.base, head, lambda sha: ['no PR']))

    def test_unrelated_baseline_is_rejected(self):
        with self.assertRaises(ValueError):
            verify_history(self.root, 'f' * 40, self.base, lambda sha: [])

    def test_symlink_media_is_structural(self):
        p = self.root / 'static/media/secret.jpg'
        p.parent.mkdir(parents=True)
        p.symlink_to('/etc/passwd')
        self.assertTrue(structural_changes(self.root, self.base, self.commit()))

    def test_review_requires_issue_worktree_checks_and_tim_merge(self):
        pr = {'base': {'ref': 'main'}, 'merged': True, 'merged_by': {'login': 'timrosenberg'},
              'body': 'Closes #2\n- [x] Worktree: /tmp/worktree\n- [x] Automated checks\n- [x] Rendered checks\n- [x] Acceptance criteria'}
        issue = {'body': 'Problem and scope. Approach, acceptance criteria, verification, compatibility and rollback. ' * 10, 'pull_request': None}
        self.assertEqual(review_errors(pr, issue, True), [])
        pr['body'] = 'Closes #2'
        self.assertTrue(review_errors(pr, issue, True))
        pr['merged_by'] = {'login': 'someone-else'}
        self.assertIn('Tim must merge', '\n'.join(review_errors(pr, issue, True)))

    def test_healthy_baseline_uses_only_successful_main_publishing_runs(self):
        valid = {'event': 'push', 'head_branch': 'main', 'conclusion': 'success', 'display_title': 'Publish ' + 'a' * 40, 'path': '.github/workflows/publish.yml', 'head_sha': 'a' * 40}
        fake = dict(valid, head_branch='feature', display_title='Publish ' + 'c' * 40)
        self.assertEqual(healthy_baseline([fake, valid], 'd' * 40), 'a' * 40)
        self.assertEqual(healthy_baseline([dict(valid, conclusion='failure')], 'd' * 40), 'd' * 40)

    def test_reviewed_recovery_can_cover_exact_earlier_direct_commit(self):
        self.put('layouts/page.html', 'changed')
        bad = self.commit()
        self.git('revert', '--no-edit', 'HEAD')
        repair = self.git('rev-parse', 'HEAD')
        def review(sha):
            return [] if sha == repair else ['unreviewed']
        claims = lambda sha: [bad] if sha == repair else []
        self.assertEqual(verify_history(self.root, self.base, repair, review, claims), [])
        self.assertTrue(verify_history(self.root, self.base, repair, lambda sha: ['unreviewed'], claims))


if __name__ == '__main__':
    unittest.main()
