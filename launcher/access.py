import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import secrets
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise ValueError('Account service redirects are not allowed')


def protect(data, decrypt=False):
    if os.name != 'nt':
        raise RuntimeError('Invitation enrollment currently requires Windows credential protection')
    class Blob(ctypes.Structure):
        _fields_ = [('size', wintypes.DWORD), ('data', ctypes.POINTER(ctypes.c_ubyte))]
    buffer = ctypes.create_string_buffer(data)
    source = Blob(len(data), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ubyte)))
    target = Blob()
    crypt = ctypes.WinDLL('crypt32', use_last_error=True)
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.LocalFree.argtypes = [ctypes.c_void_p]
    kernel.LocalFree.restype = ctypes.c_void_p
    function = crypt.CryptUnprotectData if decrypt else crypt.CryptProtectData
    function.argtypes = [ctypes.POINTER(Blob), ctypes.c_void_p, ctypes.POINTER(Blob),
                         ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(Blob)]
    function.restype = wintypes.BOOL
    if not function(ctypes.byref(source), None, None, None, None, 1, ctypes.byref(target)):
        raise RuntimeError('Windows could not protect the account access credential')
    try:
        return ctypes.string_at(target.data, target.size)
    finally:
        kernel.LocalFree(target.data)


def service_url(root):
    path = root / 'access.json'
    if not path.exists():
        path = root / 'local/access.json'
    if not path.exists():
        return None
    value = json.loads(path.read_text())
    url = value.get('url', '')
    parsed = urlsplit(url)
    if (value.get('channel') != 'area52' or parsed.scheme != 'https' or not parsed.hostname
            or parsed.username or parsed.password or parsed.query or parsed.fragment
            or parsed.path not in ('', '/')):
        raise ValueError('Invalid Area 52 access-service configuration')
    return url.rstrip('/')


class Client:
    def __init__(self, directory, url):
        self.path = Path(directory) / 'area52-access.bin'
        self.url = url

    def credential(self):
        if self.path.exists():
            saved = json.loads(protect(self.path.read_bytes(), decrypt=True))
            if saved['url'] != self.url:
                raise ValueError('Access-service address changed; contact the administrator')
            return saved['token']
        token = secrets.token_urlsafe(32)
        protected = protect(json.dumps({'url': self.url, 'token': token}).encode())
        with self.path.open('xb') as file:
            file.write(protected)
        return token

    def request(self, action, data):
        token = self.credential()
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}
        if action == 'enroll':
            data = dict(data, request_token=token)
        elif action != 'status':
            raise ValueError('Unsupported account action')
        request = Request(self.url + '/v1/area52/' + action,
                          data=json.dumps(data).encode(), headers=headers, method='POST')
        try:
            with build_opener(NoRedirect).open(request, timeout=15) as response:
                raw = response.read(8193)
                if len(raw) > 8192:
                    raise ValueError('Unexpected account-service response')
                return json.loads(raw)
        except HTTPError as error:
            raise ValueError('Account service rejected the request. Check your details or retry later.') from error
