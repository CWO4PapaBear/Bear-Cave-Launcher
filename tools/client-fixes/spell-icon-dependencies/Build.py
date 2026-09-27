"""Stage missing exact-path spell icon dependencies without changing spell data."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import struct
import sys


def digest(data):
    return hashlib.sha256(data).hexdigest()


def table(data, fields):
    magic, count, width, size, strings = struct.unpack_from('<4s4I', data)
    assert (magic, width, size) == (b'WDBC', fields, fields * 4)
    assert len(data) == 20 + count * size + strings
    rows = list(struct.iter_unpack('<' + 'I' * fields, data[20:20 + count * size]))
    assert len({r[0] for r in rows}) == count
    return rows, data[20 + count * size:]


def build(input_path, source_path, output_path, library):
    sys.path.insert(0, str(library.resolve()))
    from lib.mpq import MPQArchive, write_archive
    from PIL import Image

    assert not output_path.exists(), 'Use a new staging output'
    assert input_path.resolve() != output_path.resolve()
    before = digest(input_path.read_bytes())
    with MPQArchive(input_path) as archive:
        names = archive.read_file('(listfile)').decode().splitlines()
        files = {n: archive.read_file(n) for n in names if n != '(listfile)'}
    keys = {n.replace('/', '\\').lower(): n for n in files}
    assert len(keys) == len(files), 'Ambiguous archive names'
    spells, _ = table(files[keys['dbfilesclient\\spell.dbc']], 234)
    icons, strings = table(files[keys['dbfilesclient\\spellicon.dbc']], 2)
    used = {r[133] for r in spells} | {r[134] for r in spells}
    dependencies = {}
    for icon, offset in icons:
        assert offset < len(strings)
        path = strings[offset:].split(b'\0')[0].decode() + '.blp'
        if icon in used and path.lower().startswith('heroadvancement\\'):
            dependencies[icon] = path
    added = []
    original = dict(files)
    with MPQArchive(source_path) as source:
        for icon, path in sorted(dependencies.items()):
            data = source.read_file(path)
            Image.open(io.BytesIO(data)).load()
            if path.lower() in keys:
                assert files[keys[path.lower()]] == data, 'Existing texture differs: ' + path
                continue
            files[path] = data
            keys[path.lower()] = path
            added.append(dict(icon=icon, path=path, bytes=len(data), sha256=digest(data)))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_archive(output_path, files)
    with MPQArchive(output_path) as check:
        assert set(check.read_file('(listfile)').decode().splitlines()) == set(files) | {'(listfile)'}
        for name, data in files.items():
            assert check.read_file(name) == data, name
        for path in dependencies.values():
            assert check.has_file(path), path
    assert all(files[n] == data for n, data in original.items())
    assert digest(input_path.read_bytes()) == before
    return dict(before=before, after=digest(output_path.read_bytes()), added=added,
                existingEntriesPreserved=len(original), referencedIcons=len(dependencies))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--mpq-library', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    result = build(args.input, args.source, args.output, args.mpq_library)
    args.report.write_text(json.dumps(result, indent=2) + '\n')
    print(f"Staged {len(result['added'])} missing textures; all existing entries preserved.")
