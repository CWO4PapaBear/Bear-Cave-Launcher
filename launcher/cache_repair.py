"""Selective, local Area 52 cache recovery; never distributed cache contents."""
import os
from pathlib import Path
import struct
import tempfile
from . import updater


def parse_cache(data):
    if len(data) < 32 or data[:4] != b'BOMW' or struct.unpack_from('<I', data, 4)[0] != 12340:
        raise ValueError('Expected a 3.3.5a creaturecache.wdb')
    rows = []
    seen = set()
    offset = 24
    while offset + 8 <= len(data):
        entry, size = struct.unpack_from('<II', data, offset)
        if entry == 0:
            if size or any(data[offset:]):
                raise ValueError('Invalid cache terminator')
            return data[:24], rows, data[offset:]
        if entry in seen or size == 0 or size > len(data) - offset - 8:
            raise ValueError('Duplicate, empty or truncated cache record')
        seen.add(entry)
        rows.append((entry, data[offset:offset + 8 + size]))
        offset += 8 + size
    raise ValueError('Missing cache terminator')


def metadata(record):
    offset = 8
    for _ in range(6):
        offset = record.index(b'\0', offset) + 1
    return struct.unpack_from('<II', record, offset)


def apply(cache, before, after, check_closed):
    check_closed()
    if cache.read_bytes() != before:
        raise RuntimeError('Cache changed since inspection')
    if before == after:
        return None
    backup_fd, backup_name = tempfile.mkstemp(prefix=cache.name + '.backup-', dir=cache.parent)
    backup = Path(backup_name)
    with os.fdopen(backup_fd, 'wb') as stream:
        stream.write(before)
        stream.flush()
        os.fsync(stream.fileno())
    if backup.read_bytes() != before:
        raise RuntimeError('Backup verification failed')
    staged_fd, staged_name = tempfile.mkstemp(prefix=cache.name + '.repair-', dir=cache.parent)
    staged = Path(staged_name)
    try:
        with os.fdopen(staged_fd, 'wb') as stream:
            stream.write(after)
            stream.flush()
            os.fsync(stream.fileno())
        check_closed()
        if cache.read_bytes() != before:
            raise RuntimeError('Cache changed before replacement; backup retained')
        os.replace(staged, cache)
        if cache.read_bytes() != after:
            raise RuntimeError('Readback failed; backup retained at ' + str(backup))
    finally:
        if staged.exists():
            staged.unlink()
    return backup



def safe_path(root, path):
    for part in (path, *path.parents):
        if part.is_symlink() or (hasattr(part, 'is_junction') and part.is_junction()):
            raise ValueError('Linked cache paths are not allowed')
        if part == root:
            return
    raise ValueError('Cache path escapes client folder')


def repair(root, channel, report=lambda message: None):
    if channel != 'area52':
        return 0
    root = Path(root)
    base = root / 'Cache' / 'WDB'
    safe_path(root, base)
    if not base.exists():
        return 0
    repaired = 0
    for locale in sorted(base.iterdir()):
        safe_path(root, locale)
        if not locale.is_dir():
            continue
        for realm in ('Area 52 - Free-Pick', 'Area-52'):
            cache = locale / realm / 'creaturecache.wdb'
            safe_path(root, cache)
            if not cache.exists():
                continue
            before = cache.read_bytes()
            header, rows, tail = parse_cache(before)
            target = next((record for entry, record in rows if entry == 22313), None)
            # Unknown/current metadata is not evidence of this specific defect.
            if target is None or metadata(target) != (0, 8):
                continue
            remaining = [(entry, record) for entry, record in rows if entry != 22313]
            after = header + b''.join(record for _, record in remaining) + tail
            if parse_cache(after) != (header, remaining, tail):
                raise ValueError('Cache preservation check failed')
            def guard():
                safe_path(root, cache)
                updater.ensure_closed()
            apply(cache, before, after, guard)
            repaired += 1
    if repaired:
        report('Repaired Rumbling Earth-Heart targeting cache; other creature records preserved.')
    return repaired
