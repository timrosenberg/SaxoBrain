"""Run the publish guard against local address lists without network access."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
RETIRED = [
    '/resources/etudes',
    '/resources/etudes/27-melodious-and-rhythmical-exercises-no-1',
    '/resources/etudes/27-virtuoso-studies-no-1',
    '/resources/etudes/28-etudes-on-the-modes-of-limited-transposition',
    '/resources/etudes/50-easy-and-progressive-studies-no-2',
    '/resources/etudes/50-easy-and-progressive-studies-no-26',
    '/resources/etudes/articulation-exercise',
]


class AddressGuard(unittest.TestCase):
    def check_addresses(self, new, old):
        with tempfile.TemporaryDirectory() as tmp:
            new_path = Path(tmp) / 'new.txt'
            old_path = Path(tmp) / 'old.txt'
            new_path.write_text('\n'.join(new) + '\n')
            old_path.write_text('\n'.join(old) + '\n')
            return subprocess.run(
                ['python3', str(ROOT / 'scripts/check_addresses.py'),
                 str(new_path), 'https://example.org/', old_path.as_uri()],
                capture_output=True, text=True)

    def test_approved_retired_etude_addresses_may_disappear(self):
        result = self.check_addresses(['/'], ['/', *[a + '/' for a in RETIRED]])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('7 approved retired addresses', result.stdout)

    def test_other_addresses_under_the_retired_section_still_fail(self):
        result = self.check_addresses(['/'], ['/', *RETIRED, '/resources/etudes/another-study'])
        self.assertEqual(result.returncode, 1)
        self.assertIn('This address is live but would disappear: /resources/etudes/another-study', result.stdout)

    def test_unrelated_missing_addresses_still_fail(self):
        result = self.check_addresses(['/'], ['/', '/reading/example'])
        self.assertEqual(result.returncode, 1)
        self.assertIn('This address is live but would disappear: /reading/example', result.stdout)

    def test_duplicate_addresses_still_fail_including_retired_addresses(self):
        result = self.check_addresses(['/', RETIRED[0], RETIRED[0] + '/'], ['/'])
        self.assertEqual(result.returncode, 1)
        self.assertIn('Two pages claim the same address: /resources/etudes', result.stdout)


if __name__ == '__main__':
    unittest.main()
