import errno
import hashlib
import os
import shutil
import sys
import tempfile
from pathlib import Path

from .backups import plain_tree, linked


def launcher_home():
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


def state_path(client):
    client = Path(client).resolve()
    home = launcher_home()
    base = home / '.bear-cave-launcher'
    if home == client:
        return base
    identity = hashlib.sha256(os.fsencode(os.path.normcase(str(client)))).hexdigest()[:24]
    return base / 'clients' / identity


def inventory(path):
    plain_tree(path)
    result = {}
    for item in path.rglob('*'):
        value = None
        if item.is_file():
            with item.open('rb') as stream:
                value = hashlib.file_digest(stream, 'sha256').digest()
        result[item.relative_to(path)] = value
    return result


def migrate(client):
    destination = state_path(client)
    legacy = client / '.bear-cave-launcher'
    held = client / '.bear-cave-launcher.migrating'
    for path in (launcher_home() / '.bear-cave-launcher', destination.parent, destination, legacy, held):
        if path.is_symlink() or (path.exists() and linked(path)):
            raise ValueError('Linked launcher state is not allowed')
    if legacy == destination or not (legacy.exists() or held.exists()):
        return destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    if legacy.exists():
        if held.exists() or destination.exists():
            raise ValueError('Conflicting client state folders; both have been preserved')
        plain_tree(legacy)
        legacy.rename(held)
    if not destination.exists():
        try:
            held.rename(destination)
            return destination
        except OSError as error:
            if error.errno != errno.EXDEV and getattr(error, 'winerror', None) != 17:
                raise
        with tempfile.TemporaryDirectory(dir=destination.parent) as temporary:
            copy = Path(temporary) / 'state'
            shutil.copytree(held, copy)
            if inventory(copy) != inventory(held):
                raise ValueError('Client state changed during migration')
            copy.rename(destination)
    if inventory(held) != inventory(destination):
        raise ValueError('Interrupted client state migration differs; both copies have been preserved')
    shutil.rmtree(held)
    return destination


def replace_client_file(source, target, expected):
    if source.stat().st_dev == target.parent.stat().st_dev:
        os.replace(source, target)
        return
    fd, name = tempfile.mkstemp(dir=target.parent)
    os.close(fd)
    temporary = Path(name)
    try:
        shutil.copy2(source, temporary)
        with temporary.open('rb') as stream:
            if hashlib.file_digest(stream, 'sha256').hexdigest() != expected:
                raise ValueError('Client file changed during cross-volume copy')
        os.replace(temporary, target)
        source.unlink()
    finally:
        temporary.unlink(missing_ok=True)
