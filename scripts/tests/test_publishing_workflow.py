"""Guard the production trust boundary and validation ordering."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[2]


class PublishingWorkflow(unittest.TestCase):
    def setUp(self):
        self.workflow = yaml.load((ROOT / '.github/workflows/publish.yml').read_text(), Loader=yaml.BaseLoader)

    def test_global_permissions_are_read_only(self):
        self.assertEqual(self.workflow['permissions'], {'contents': 'read'})

    def test_all_main_pushes_and_prs_validate_without_path_skips(self):
        events = self.workflow['on']
        self.assertEqual(events['push']['branches'], ['main'])
        self.assertIn('pull_request', events)
        self.assertNotIn('paths', events['push'])
        self.assertNotIn('paths', events['pull_request'])
        self.assertEqual(self.workflow['jobs']['validate']['name'], 'Validate site')
        self.assertEqual(self.workflow['jobs']['validate']['permissions']['pull-requests'], 'read')
        self.assertEqual(self.workflow['jobs']['validate']['permissions']['issues'], 'read')

    def test_only_validated_main_can_deploy(self):
        jobs = self.workflow['jobs']
        self.assertEqual(jobs['deploy']['needs'], ['validate'])
        self.assertIn("refs/heads/main", jobs['deploy']['if'])
        self.assertIn('pull_request', jobs['deploy']['if'])
        self.assertEqual(jobs['deploy']['environment']['name'], 'github-pages')
        self.assertEqual(jobs['deploy']['permissions']['pages'], 'write')
        self.assertTrue(all(value == 'read' for value in jobs['validate']['permissions'].values()))

    def test_source_is_not_executed_in_the_deployment_job(self):
        steps = self.workflow['jobs']['deploy']['steps']
        self.assertFalse(any(step.get('with', {}).get('ref') == '${{ inputs.revision }}' for step in steps))
        self.assertTrue(any('smoke_site.py' in step.get('run', '') for step in steps))

    def test_policy_gate_precedes_build(self):
        steps = self.workflow['jobs']['validate']['steps']
        runs = [step.get('run', '') for step in steps]
        gate = next(i for i, run in enumerate(runs) if 'publishing_policy.py' in run)
        build = next(i for i, run in enumerate(runs) if 'run_validation.py' in run)
        self.assertLess(gate, build)

    def test_validation_does_not_rebuild_a_broken_push_parent(self):
        workflow = (ROOT / '.github/workflows/publish.yml').read_text()
        self.assertNotIn('github.event.before', workflow)
        self.assertIn('--baseline-only', workflow)


if __name__ == '__main__':
    unittest.main()
