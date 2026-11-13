import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from launcher import app,connection
class DefaultRealmTests(unittest.TestCase):
    def test_saved_folder_recovers_and_local_overrides_win(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'endpoint-migrations.json').write_text(json.dumps(dict(schema=1,routes=[],area52_default='test.example:3725')))
            client=root/'game';client.mkdir();(client/'Data').mkdir()
            (root/'settings.json').write_text(json.dumps(dict(channel='area52',area52_client=str(client))))
            with patch.object(app,'ROOT',root):
                instance=app.Application(root)
                state=instance.status()
                self.assertTrue(state['channel_ready'] and state['client'] and not state['busy'])
                self.assertEqual(instance.realm(),'test.example:3725')
                with self.assertRaises(ValueError):connection.load(root,'ptr')
                (root/'connection.json').write_text(json.dumps(dict(schema=1,channel='ptr',address='private.example:3724')))
                self.assertEqual(instance.realm(),'private.example:3725')
                (root/'connection-area52.json').write_text(json.dumps(dict(schema=1,channel='area52',address='127.0.0.1:3726')))
                self.assertEqual(instance.realm(),'127.0.0.1:3726')
