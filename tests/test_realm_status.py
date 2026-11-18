import unittest
from launcher.realm_status import validate
class StatusTests(unittest.TestCase):
 def test_human_count(self):
  self.assertEqual(validate(dict(environment='cloud',timestamp=100,online=True,players=4), 'cloud',110),dict(state='online',players=4))
 def test_stale_wrong_and_invalid(self):
  for changes in [dict(timestamp=0),dict(environment='development'),dict(players=-1),dict(players=True),dict(online='true')]:
   with self.assertRaises(ValueError):validate(dict(environment='cloud',timestamp=100,online=True,players=4,**{})|changes,'cloud',110)
 def test_offline_zero(self):
  self.assertEqual(validate(dict(environment='cloud',timestamp=100,online=False,players=4),'cloud',110)['players'],0)
