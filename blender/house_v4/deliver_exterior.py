"""Run the native B render and verified frontend export as one resumable job."""
import argparse
import ctypes
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from exterior_delivery import ANIMATION, OUT, REVISION, ROOT, identity, write_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--blender', required=True, type=Path)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    node = shutil.which('node')
    if not args.blender.is_file() or not node:
        raise RuntimeError('Blender and Node must be installed before delivery.')
    if not ANIMATION.is_file():
        raise RuntimeError('Approved native animation is missing.')
    delivery = ROOT/'blender/house_v4/exterior_delivery.py'
    stages = [
        ('rendering', [str(args.blender), '-b', str(ANIMATION), '--python-exit-code', '1',
                       '--python', str(delivery), '--', '--render', '--resume']),
        ('exporting', [sys.executable, str(delivery), '--export']),
        ('testing', [node, 'node_modules/vitest/vitest.mjs', 'run']),
        ('checking', [node, 'node_modules/astro/bin/astro.mjs', 'check']),
        ('building', [node, 'node_modules/astro/bin/astro.mjs', 'build']),
    ]
    if args.dry_run:
        print(json.dumps({'identity': identity(), 'stages': stages}, indent=2))
        return
    OUT.mkdir(parents=True, exist_ok=True)
    # An OS lock is released even if the process crashes; it prevents two jobs
    # from rendering or activating the same revision at the same time.
    with (OUT/'pipeline.lock').open('a+b') as lock:
        lock.seek(0)
        if not lock.read(1):
            lock.write(b'0')
            lock.flush()
        lock.seek(0)
        if os.name == 'nt':
            import msvcrt
            msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
        else:
            import fcntl
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        status = {'revision': REVISION, 'pid': os.getpid(), 'startedAt': now(), 'stages': []}
        try:
            for phase, command in stages:
                status.update(phase=phase, updatedAt=now())
                write_json(OUT/'pipeline-status.json', status)
                with (OUT/f'pipeline-{phase}.log').open('a', encoding='utf-8') as log:
                    result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                status['stages'].append({'phase': phase, 'exitCode': result.returncode, 'finishedAt': now()})
                if result.returncode:
                    raise RuntimeError(f'{phase} failed ({result.returncode}); see pipeline-{phase}.log')
            manifest = json.loads((ROOT/'src/config/house-v4-manifest.json').read_text())
            if manifest['revision'] != REVISION:
                raise RuntimeError('Frontend revision changed before completion.')
            report_path = OUT.parent/'artifact-manifest.json'
            if report_path.exists():
                report = json.loads(report_path.read_text(encoding='utf-8'))
                report.update(websiteSequenceUpdated=True,
                              frontendDelivery={'revision': REVISION, 'report': 'frontend/export-report.json'})
                write_json(report_path, report)
            status.update(phase='complete', updatedAt=now())
            write_json(OUT/'pipeline-status.json', status)
        except BaseException as error:
            status.update(phase='failed', error=str(error), updatedAt=now())
            write_json(OUT/'pipeline-status.json', status)
            raise
        finally:
            if os.name == 'nt':
                ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


if __name__ == '__main__':
    main()
