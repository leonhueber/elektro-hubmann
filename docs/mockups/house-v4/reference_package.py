"""Seal or verify the selected V4 reference; standard library only.

Run --seal once after preparing the complete handoff, then use --verify.
Further design work belongs in a new revision folder, not in this baseline.
"""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
REVISION = 'v4-reference-01'
LOCK = ROOT / 'reference-lock.json'
HANDOFF = REPO / 'docs/14-haus-v4-verbindliche-vorlage-und-kamerafahrten.md'
ARCHIVE = REPO / 'assets/reference/house-v4-reference-01.zip'
RECEIPT = ARCHIVE.with_suffix('.zip.sha256')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def relative(path):
    return path.relative_to(REPO).as_posix()


def sources():
    files = []
    for path in ROOT.rglob('*'):
        if path == LOCK or '__pycache__' in path.parts:
            continue
        if path.suffix in {'.log', '.pyc', '.pyo', '.pending', '.tmp'}:
            continue
        require(not path.is_symlink(), f'Reference must contain original files: {path}')
        if path.is_file():
            files.append(path)
    require(HANDOFF.is_file(), 'Missing modelling/camera handoff.')
    files.append(HANDOFF)
    return sorted(files, key=relative)


def check_content():
    for folder, pattern, count in [
        ('states', '*.png', 8), ('website-mockups', '*.png', 11),
        ('prompts', '*.txt', 9), ('references', '*.woff2', 14),
    ]:
        require(len(list((ROOT / folder).glob(pattern))) == count,
                f'Expected {count} {pattern} files in {folder}.')
    for name in ['09-grundriss-eg.svg', '10-grundriss-og.svg', 'website.html',
                 'website-reference.css', 'review-board.html', 'references/logo.png']:
        require((ROOT / name).is_file(), f'Missing reference: {name}')

    plan = json.loads((ROOT / 'motion-plan.json').read_text(encoding='utf-8'))
    require(plan['status'] == 'planned_not_implemented', 'Motion is a plan, not an implemented camera.')
    require(plan['referenceRevision'] == REVISION, 'Wrong motion reference revision.')
    poses = {pose['id']: pose for pose in plan['poses']}
    require(len(poses) == 8, 'Expected eight distinct target poses.')
    for pose in poses.values():
        for key in ['image', 'websiteReference']:
            require((ROOT / pose[key]).is_file(), f'Missing pose reference: {pose[key]}')
        require(pose['cameraWorldPosition'] is None and pose['cameraTargetPosition'] is None,
                'Exact coordinates must be solved in the future native model.')
    known = set(poses) | {p['id'] for p in plan['intermediatePoses']}
    require(len(plan['timeline']) == 18, 'Expected eighteen motion/hold segments.')
    cursor = 0
    for segment in plan['timeline']:
        require(segment['start'] == cursor and segment['end'] > cursor,
                f'Timeline gap or overlap: {segment["id"]}')
        require(segment['from'] in known and segment['to'] in known, 'Unknown motion pose.')
        cursor = segment['end']
    require(cursor == 1, 'Timeline must end at 100%.')
    require(len(plan['navigation']) == 6, 'Expected six navigation chapters.')
    for item in plan['navigation']:
        require(any(s['kind'] == 'hold' and s['to'] == item['pose']
                    and s['chapterIndex'] == item['chapterIndex']
                    and s['start'] < item['progress'] < s['end']
                    for s in plan['timeline']), 'Navigation must land inside its matching hold.')
    preview = plan['preview']
    require(preview['timelinePositionCount'] - 1 == preview['fps'] * preview['durationSeconds'],
            'Preview duration and inclusive timeline samples disagree.')


def check_archive(path, manifest, lock_bytes):
    with ZipFile(path) as archive:
        expected = [entry['path'] for entry in manifest['files']] + [relative(LOCK)]
        require(sorted(archive.namelist()) == sorted(expected), 'Archive inventory differs.')
        require(archive.read(relative(LOCK)) == lock_bytes, 'Archive lock differs from source lock.')
        for entry in manifest['files']:
            data = archive.read(entry['path'])
            require(len(data) == entry['bytes'] and digest(data) == entry['sha256'],
                    f'Archive checksum mismatch: {entry["path"]}')


def seal():
    pending = ARCHIVE.with_suffix('.zip.pending')
    require(not any(p.exists() for p in [LOCK, ARCHIVE, RECEIPT, pending]),
            'Reference already sealed or packaging incomplete. Do not overwrite; use a new revision.')
    check_content()
    # Read once so each checksum and archived image refer to the exact same bytes.
    payload = {relative(path): path.read_bytes() for path in sources()}
    manifest = {
        'schemaVersion': 1,
        'referenceRevision': REVISION,
        'status': 'selected_visual_reference',
        'sealedAtUtc': datetime.now(timezone.utc).isoformat(),
        'archivePath': relative(ARCHIVE),
        'archiveReceiptPath': relative(RECEIPT),
        'scope': 'Original mockups, frontend screenshots/assets, plans, prompts and modelling/camera handoff.',
        'animationStatus': 'planned_not_implemented',
        'fileCount': len(payload),
        'totalSourceBytes': sum(len(data) for data in payload.values()),
        'files': [{'path': name, 'bytes': len(data), 'sha256': digest(data)}
                  for name, data in payload.items()],
    }
    lock_bytes = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(pending, 'x', compression=ZIP_DEFLATED, compresslevel=6) as archive:
        for name, data in payload.items():
            archive.writestr(name, data)
        archive.writestr(relative(LOCK), lock_bytes)
    check_archive(pending, manifest, lock_bytes)
    # Refuse to publish a baseline if any source changed while packaging.
    for name, data in payload.items():
        require((REPO / name).read_bytes() == data, f'Source changed while sealing: {name}')
    pending.rename(ARCHIVE)
    with LOCK.open('xb') as output:
        output.write(lock_bytes)
    with RECEIPT.open('x', encoding='ascii', newline='\n') as output:
        output.write(f'{digest(ARCHIVE.read_bytes())}  {ARCHIVE.name}\n')
    verify()


def verify():
    require(LOCK.is_file() and ARCHIVE.is_file() and RECEIPT.is_file(), 'Reference package is incomplete.')
    check_content()
    lock_bytes = LOCK.read_bytes()
    manifest = json.loads(lock_bytes)
    require(manifest['referenceRevision'] == REVISION, 'Wrong reference lock revision.')
    require(manifest['fileCount'] == len(manifest['files']), 'Wrong inventory count.')
    require(manifest['totalSourceBytes'] == sum(e['bytes'] for e in manifest['files']), 'Wrong byte total.')
    require(sorted(relative(path) for path in sources()) == sorted(e['path'] for e in manifest['files']),
            'Source inventory changed; preserve the selected baseline and work in a new revision.')
    for entry in manifest['files']:
        data = (REPO / entry['path']).read_bytes()
        require(len(data) == entry['bytes'] and digest(data) == entry['sha256'],
                f'Source checksum mismatch: {entry["path"]}')
    expected_receipt = f'{digest(ARCHIVE.read_bytes())}  {ARCHIVE.name}'
    require(RECEIPT.read_text(encoding='ascii').strip() == expected_receipt, 'ZIP checksum mismatch.')
    check_archive(ARCHIVE, manifest, lock_bytes)
    print(json.dumps({'verified': True, 'revision': REVISION, 'files': manifest['fileCount'],
                      'originalMockups': 8, 'websiteScreenshots': 11, 'floorplans': 2,
                      'motionSegments': 18, 'archive': relative(ARCHIVE),
                      'archiveBytes': ARCHIVE.stat().st_size}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--seal', action='store_true', help='Create the baseline once; refuses to overwrite.')
    mode.add_argument('--verify', action='store_true', help='Read-only checksum and content verification.')
    args = parser.parse_args()
    try:
        seal() if args.seal else verify()
    except (ValueError, OSError, KeyError) as exc:
        parser.exit(1, f'Reference error: {exc}\n')
