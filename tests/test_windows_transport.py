import errno
import io
import json
import ssl
import unittest
from urllib.error import URLError
from urllib.request import Request
from unittest.mock import MagicMock, patch

from launcher import selfupdate, transport, updater


class WindowsTransportTests(unittest.TestCase):
    def worker(self, data, exit_code=0):
        worker = MagicMock()
        worker.__enter__.return_value = worker
        worker.stdout = io.BytesIO(data)
        worker.wait.return_value = exit_code
        worker.poll.return_value = exit_code
        return worker

    def test_forced_play_check_and_client_feed_retry_missing_file(self):
        info = dict(schema=1, enabled=True, platform='win32', build=selfupdate.BUILD,
                    version=selfupdate.VERSION, bytes=123, sha256='0'*64,
                    url=f'https://github.com/{updater.REPOSITORY}/releases/download/launcher-{selfupdate.VERSION}/BearCaveLauncher-update-win32.zip')
        failure = URLError(FileNotFoundError(errno.ENOENT, 'No such file or directory'))
        with patch.object(transport.sys, 'platform', 'win32'), patch.dict(transport.os.environ, SystemRoot='C:/Windows'), \
             patch.object(selfupdate.sys, 'frozen', True, create=True), \
             patch.object(transport, 'python_open', side_effect=failure), \
             patch.object(transport.subprocess, 'Popen', side_effect=[
                 self.worker(json.dumps(info).encode()), self.worker(b'client feed')]) as launch:
            self.assertFalse(selfupdate.startup(force=True))
            self.assertEqual(updater.fetch('https://example.org/feed'), b'client feed')
        for call in launch.call_args_list:
            args = call.args[0]
            self.assertEqual(args[args.index('--proto-redir')+1], '=https')
            self.assertNotIn('--insecure', args)

    def test_native_failure_blocks_play_and_reports_phase(self):
        with patch.object(transport.sys, 'platform', 'win32'), patch.dict(transport.os.environ, SystemRoot='C:/Windows'), \
             patch.object(selfupdate.sys, 'frozen', True, create=True), patch.object(selfupdate, 'log') as log, \
             patch.object(transport, 'python_open', side_effect=FileNotFoundError(errno.ENOENT, 'missing')), \
             patch.object(transport.subprocess, 'Popen', return_value=self.worker(b'', 60)):
            with self.assertRaisesRegex(RuntimeError, 'read launcher channel.*curl exit 60'):
                selfupdate.startup(force=True)
        self.assertIn('read launcher channel', log.call_args.args[0])

    def test_python_certificate_rejection_is_preserved(self):
        error = URLError(ssl.SSLCertVerificationError(1, 'certificate verify failed'))
        with patch.object(transport.sys, 'platform', 'win32'), patch.object(transport, 'python_open', side_effect=error), \
             patch.object(transport.subprocess, 'Popen') as launch:
            with self.assertRaises(URLError):
                with transport.urlopen(Request('https://example.org/'), 5):
                    self.fail('certificate rejection returned a response')
            launch.assert_not_called()
