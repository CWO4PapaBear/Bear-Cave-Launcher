"""HTTPS reads for the packaged Windows launcher."""
import errno
import os
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from urllib.request import urlopen as python_open, build_opener, HTTPRedirectHandler

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise ValueError("HTTPS redirects are not allowed")


class CurlResponse:
    def __init__(self, process, url):
        self.process = process
        self.url = url
        self.headers = {}

    def read(self, size):
        data = self.process.stdout.read(size)
        if len(data) < size:
            code = self.process.wait()
            if code:
                raise OSError(f'Windows HTTPS request failed (curl exit {code})')
        return data


@contextmanager
def urlopen(request, timeout, allow_redirects=True):
    try:
        response = (python_open if allow_redirects else build_opener(NoRedirect()).open)(request, timeout=timeout)
    except OSError as error:
        cause = getattr(error, 'reason', error)
        if sys.platform != 'win32' or getattr(cause, 'errno', None) != errno.ENOENT:
            raise
        if not request.full_url.startswith('https://') or request.get_method() != 'GET':
            raise
    else:
        with response:
            yield response
        return

    windows = Path(os.environ['SystemRoot'])
    executable = windows / 'Sysnative' / 'curl.exe'
    if not executable.is_file():
        executable = windows / 'System32' / 'curl.exe'
    args = [str(executable), '-q', '--globoff', '--silent', '--fail', '--location',
            '--proto', '=https', '--proto-redir', '=https', '--connect-timeout', str(timeout),
            '--speed-time', str(timeout), '--speed-limit', '1']
    if not allow_redirects:
        args.extend(['--max-redirs','0','--max-time',str(timeout)])
    for name, value in request.header_items():
        if name.lower() in ('user-agent', 'cache-control'):
            args.extend(['--header', f'{name}: {value}'])
    args.extend(['--', request.full_url])
    with subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                          creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)) as process:
        try:
            yield CurlResponse(process, request.full_url)
        finally:
            if process.poll() is None:
                process.kill()
