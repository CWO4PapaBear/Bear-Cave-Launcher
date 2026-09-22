import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from announce_ptr import payload

class AnnouncementTests(unittest.TestCase):
    def test_long_notes_fit_and_mentions_disabled(self):
        p = payload({'tag':'ptr-test','version':'test'}, '@everyone\n' * 2000)
        self.assertEqual(p['allowed_mentions'], {'parse': []})
        self.assertLessEqual(len(p['embeds'][0]['description']), 4096)
        self.assertIn('full patch notes', p['embeds'][0]['description'])

    def test_short_notes_preserved(self):
        p = payload({'tag':'ptr-test','version':'test'}, 'Fixes and testing instructions')
        self.assertEqual(p['embeds'][0]['description'], 'Fixes and testing instructions')
        self.assertIn('/releases/tag/ptr-test', p['embeds'][0]['url'])
