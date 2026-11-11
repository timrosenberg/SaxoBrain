"""Repository settings must preserve the direct content path."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from configure_publishing import rules, settings_errors


class PublishingSettings(unittest.TestCase):
    def test_main_rules_allow_content_pushes(self):
        main, = rules()
        self.assertEqual(main['conditions']['ref_name']['include'], ['refs/heads/main'])
        self.assertEqual({r['type'] for r in main['rules']}, {'non_fast_forward', 'deletion'})

    def test_environment_must_exclude_main_and_all_other_branches(self):
        self.assertEqual(settings_errors(rules(), [{'name': 'main', 'type': 'branch'}]), [])
        self.assertTrue(settings_errors(rules(), [{'name': 'feature', 'type': 'branch'}]))
        self.assertTrue(settings_errors(rules(), [{'name': 'main', 'type': 'branch'}, {'name': '*', 'type': 'branch'}]))

    def test_modified_main_rule_is_detected(self):
        current = rules()
        current[0]['rules'] = []
        self.assertTrue(settings_errors(current, [{'name': 'main', 'type': 'branch'}]))


if __name__ == '__main__':
    unittest.main()
