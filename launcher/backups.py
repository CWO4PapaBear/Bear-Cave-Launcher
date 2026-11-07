"""Retention for completed launcher updates."""
import json
import os
import re
import shutil
import stat
import time
from pathlib import Path


WORK = re.compile(r'bcu-[0-9a-f]{12}')
SNAPSHOT = re.compile(r'[0-9]{20}-bcu-[0-9a-f]{12}')
RECEIPT = '.bear-cave-backup.json'


def linked(path):
    attributes = getattr(path.lstat(), 'st_file_attributes', 0)
    return path.is_symlink() or bool(attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def plain_tree(path):
    if linked(path):
        raise ValueError(f'Linked update path: {path}')
    if path.is_dir():
        for item in path.iterdir():
            plain_tree(item)


def owned(snapshot, root):
    marker = snapshot / RECEIPT
    if not (SNAPSHOT.fullmatch(snapshot.name) and snapshot.is_dir() and not linked(snapshot)
            and marker.is_file() and not linked(marker)):
        return False
    try:
        return json.loads(marker.read_text()) == {'installation': str(root), 'snapshot': snapshot.name}
    except ValueError:
        return False


def collect(root, log):
    root = root.resolve(strict=True)
    lock = root.parent / (root.name + '.update-lock')
    if not (root / 'Backups').is_dir() and not any(root.parent.glob('bcu-*')):
        return
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return
    try:
        os.close(fd)
        collect_locked(root, log)
    finally:
        lock.unlink()


def collect_locked(root, log):
    history = root / 'Backups'
    if history.is_symlink() or (history.exists() and (linked(history) or not history.is_dir())):
        raise ValueError('Invalid launcher backup directory')
    for work in root.parent.glob('bcu-*'):
        if not WORK.fullmatch(work.name) or linked(work) or not work.is_dir():
            continue
        job = work / 'job.json'
        ready = work / 'worker-ready'
        if not job.is_file() or linked(job) or not ready.is_file() or linked(ready):
            continue
        try:
            target = Path(json.loads(job.read_text())['root'])
        except (OSError, ValueError, TypeError, KeyError):
            continue
        if target != root or (work / 'failed').exists() or (work / 'payload').exists():
            continue
        if any(linked(child) for child in work.iterdir()):
            continue
        previous = work / 'previous'
        completed = work / 'backup-retained'
        if previous.is_dir():
            plain_tree(previous)
            if not (previous / 'BearCaveLauncher.exe').is_file() or not (previous / 'launcher-version.json').is_file():
                continue
            history.mkdir(exist_ok=True)
            old_history = previous / 'Backups'
            if old_history.exists():
                for item in old_history.iterdir():
                    if (history / item.name).exists():
                        raise ValueError(f'Conflicting backup history: {item.name}')
                    item.rename(history / item.name)
                old_history.rmdir()
            name = f'{ready.stat().st_mtime_ns:020d}-{work.name}'
            destination = history / name
            receipt = {'installation': str(root), 'snapshot': name}
            marker = previous / RECEIPT
            if marker.exists() and json.loads(marker.read_text()) != receipt:
                raise ValueError('Conflicting launcher backup receipt')
            if destination.exists():
                raise ValueError('Existing launcher backup destination')
            marker.write_text(json.dumps(receipt))
            # Record the destination before the rename so cleanup can resume after interruption.
            completed.write_text(name)
            previous.rename(destination)
        if completed.is_file() and not linked(completed):
            name = completed.read_text()
            if not SNAPSHOT.fullmatch(name) or not owned(history / name, root):
                continue
            names = {p.name for p in work.iterdir()}
            if names <= {'download.zip','runner','worker-ready','job.json','backup-retained'}:
                plain_tree(work)
                # The restarting worker may still have its executable open on Windows.
                # Leave the ownership records intact until its runner is gone.
                runner = work / 'runner'
                for attempt in range(8):
                    try:
                        if runner.exists():
                            shutil.rmtree(runner)
                        break
                    except PermissionError:
                        if attempt == 7:
                            raise
                        time.sleep(.25)
                shutil.rmtree(work)
    if history.is_dir():
        backups = sorted((item for item in history.iterdir() if owned(item, root)), reverse=True)
        for obsolete in backups[2:]:
            plain_tree(obsolete)
            shutil.rmtree(obsolete)
        if backups:
            log(f'Launcher backup history: {history} ({min(len(backups), 2)} retained)')
