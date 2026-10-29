import json, unittest
from test_connection import test_directory
from launcher import connection

class EndpointTests(unittest.TestCase):
    def test_preserved_old_settings_resolve_only_area52(self):
        with test_directory() as root:
            config=json.dumps(dict(schema=1,channel='ptr',address='old.example'))
            (root/'connection.json').write_text(config)
            migrations={'schema':1,'routes':[dict(channel='area52',before='old.example:3725',after='new.example:3725')]}
            (root/'endpoint-migrations.json').write_text(json.dumps(migrations))
            self.assertEqual(connection.load(root,'area52'),'new.example:3725')
            self.assertEqual(connection.load(root,'ptr'),'old.example')
            self.assertEqual((root/'connection.json').read_text(),config)
            for value in ('127.0.0.1:3725','192.168.1.15:3725','custom.example:3725','new.example:3725','old.example:3726'):
                (root/'connection-area52.json').write_text(json.dumps(dict(schema=1,channel='area52',address=value)))
                self.assertEqual(connection.load(root,'area52'),value)
            (root/'connection-area52.json').write_text(json.dumps(dict(schema=1,channel='area52',address='old.example:3725')))
            self.assertEqual(connection.load(root,'area52'),'new.example:3725')
            migrations['routes']*=2
            (root/'endpoint-migrations.json').write_text(json.dumps(migrations))
            with self.assertRaises(ValueError):connection.load(root,'area52')
