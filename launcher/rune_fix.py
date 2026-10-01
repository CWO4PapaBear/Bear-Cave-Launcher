"""Exact-build, two-byte client rune recovery repair. No executable download."""
import hashlib

FIX_ID = 'rune-recovery-v1'
BEFORE = 'aa63a5750d60ef16746c686b3d5e26876d98953eab08b1c026cd0faf78e88cb8'
AFTER = '64be3b76bd0365b420a2448e53bca9e15949b28ace5e8aac626ffb1757d080c9'
OFFSET = 3309220
SIZE = 7704216
WARMANE_BEFORE = 'bf644876709c591acc17c0da8cdf1814edcc9f1e6bc109a8c0d5c38c79dc953c'
WARMANE_AFTER = '0d1cce504f8ee236719897bf7433a27cba9e275e6d26ef57367bec4f455128d9'
WARMANE_SIZE = 7699456

def patched(data):
    digest = hashlib.sha256(data).hexdigest()
    builds = {BEFORE: (SIZE, AFTER), WARMANE_BEFORE: (WARMANE_SIZE, WARMANE_AFTER)}
    if digest in (AFTER, WARMANE_AFTER):
        return None
    reviewed = builds.get(digest)
    if reviewed is None or len(data) != reviewed[0]:
        raise ValueError('Rune repair: this Wow.exe version has not been reviewed '
                         '(SHA256 '+digest+'). No executable changes made. '
                         'Send this hash to the Bear Cave administrator.')
    if data[OFFSET-3:OFFSET+8] != bytes.fromhex('83fb06755a8b1d8843c200'):
        raise ValueError('Rune repair instruction mismatch')
    result = data[:OFFSET] + b'\x90\x90' + data[OFFSET+2:]
    if hashlib.sha256(result).hexdigest() != reviewed[1]:
        raise ValueError('Rune repair output checksum mismatch')
    return result

def target(root):
    path = root/'Wow.exe'
    if path.is_symlink() or (hasattr(path, 'is_junction') and path.is_junction()):
        raise ValueError('Linked executable is not supported')
    if path.resolve().parent != root.resolve() or not path.is_file():
        raise ValueError('Missing or unsafe Wow.exe')
    return path

def needed(root, manifest):
    if FIX_ID not in manifest.get('client_fixes', []):
        return False
    return patched(target(root).read_bytes()) is not None
