"""Deliver Smart Home A alongside the ongoing B render, then switch atomically."""
import argparse
import ctypes
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

from smarthome_delivery import delivery, BASE_OUT, REVISION, validate_source


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def publish(expected_head):
    """Explicit opt-in: publish only this verified output, from the reviewed commit."""
    def git(*args):
        result = subprocess.run(['git', '-c', 'safe.directory='+delivery.ROOT.as_posix(), *args],
            cwd=delivery.ROOT, capture_output=True, text=True, encoding='utf-8')
        if result.returncode:
            raise RuntimeError(f'git {args[0]} failed: {result.stderr.strip()}')
        return result.stdout.strip()
    if git('rev-parse', 'HEAD') != expected_head or git('branch', '--show-current') != 'main':
        raise RuntimeError('Checkout changed during rendering; generated assets remain local for review.')
    if git('remote', 'get-url', 'origin') != 'https://github.com/leonhueber/elektro-hubmann.git':
        raise RuntimeError('Publish destination changed.')
    if git('diff', '--cached', '--name-only'):
        raise RuntimeError('Index contains other staged work; refusing to include it in the render commit.')
    validate_source()
    report_path = delivery.OUT/'export-report.json'
    report = json.loads(report_path.read_text(encoding='utf-8'))
    for profile, config in report['profiles'].items():
        folder = delivery.ROOT/'public'/delivery.MANIFEST['assetPath']/profile
        if set(p.name for p in folder.iterdir()) != set(config['sha256']):
            raise RuntimeError('Unexpected files in generated image directory.')
        for name, digest in config['sha256'].items():
            if delivery.sha(folder/name) != digest:
                raise RuntimeError('Generated image changed after validation: '+name)
    manifest_path = delivery.ROOT/'src/config/house-v4-manifest.json'
    aliases_path = delivery.ROOT/'src/config/house-v4-frames.json'
    if json.loads(manifest_path.read_text(encoding='utf-8')) != delivery.MANIFEST:
        raise RuntimeError('Website manifest changed after export.')
    if json.loads(aliases_path.read_text(encoding='utf-8')) != {
            p: delivery.schedule()[1] for p in delivery.MANIFEST['profiles']}:
        raise RuntimeError('Website frame map changed after export.')
    paths = [str(p.relative_to(delivery.ROOT)) for p in [manifest_path, aliases_path, report_path]]
    paths.append('public/'+delivery.MANIFEST['assetPath'])
    allowed = {p.relative_to(delivery.ROOT).as_posix() for p in [manifest_path, aliases_path, report_path]}
    allowed.update('public/'+delivery.MANIFEST['assetPath']+profile+'/'+name
                   for profile, config in report['profiles'].items() for name in config['sha256'])
    git('add', '--', *paths)
    if not set(git('diff', '--cached', '--name-only').splitlines()) <= allowed:
        raise RuntimeError('Other files were staged during publishing; refusing to commit them.')
    if git('rev-parse', 'HEAD') != expected_head:
        raise RuntimeError('Checkout changed during publishing.')
    git('commit', '-m', 'feat: publish native Smart Home A scroll frames')
    commit = git('rev-parse', 'HEAD')
    git('push', 'origin', commit+':refs/heads/main')
    if git('ls-remote', 'origin', 'refs/heads/main').split()[0] != commit:
        raise RuntimeError('Remote commit could not be verified after push.')
    return commit


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--blender', required=True, type=Path)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--publish-from', help='Explicitly authorize commit/push of verified render assets from this unchanged main commit.')
    args = parser.parse_args()
    node = shutil.which('node')
    if not args.blender.is_file() or not node or not delivery.SOURCE.is_file():
        raise RuntimeError('Blender, Node and both saved native Smart Home files are required.')
    validate_source()
    script = delivery.ROOT/'blender/house_v4/smarthome_delivery.py'
    stages = [
        ('rendering', [str(args.blender), '-b', str(delivery.ANIMATION), '--python-exit-code', '1',
                       '--python', str(script), '--', '--render', '--resume']),
        ('waiting_for_exterior', None),
        ('reusing', [sys.executable, str(script), '--reuse']),
        ('exporting', [sys.executable, str(script), '--export']),
        ('testing', [node, 'node_modules/vitest/vitest.mjs', 'run']),
        ('checking', [node, 'node_modules/astro/bin/astro.mjs', 'check']),
        ('building', [node, 'node_modules/astro/bin/astro.mjs', 'build']),
    ]
    if args.dry_run:
        print(json.dumps({'identity': delivery.identity(), 'stages': stages}, indent=2))
        return
    delivery.OUT.mkdir(parents=True, exist_ok=True)
    with (delivery.OUT/'pipeline.lock').open('a+b') as lock:
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
                delivery.write_json(delivery.OUT/'pipeline-status.json', status)
                if command is None:
                    deadline = time.monotonic()+24*60*60
                    while True:
                        base = json.loads((BASE_OUT/'pipeline-status.json').read_text(encoding='utf-8'))
                        if base['phase'] == 'complete':
                            break
                        if base['phase'] == 'failed' or time.monotonic() > deadline:
                            raise RuntimeError('Exterior dependency did not complete; resume after fixing its reported failure.')
                        time.sleep(15)
                    code = 0
                else:
                    with (delivery.OUT/f'pipeline-{phase}.log').open('a', encoding='utf-8') as log:
                        code = subprocess.run(command, cwd=delivery.ROOT, stdout=log, stderr=subprocess.STDOUT,
                            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0).returncode
                status['stages'].append({'phase': phase, 'exitCode': code, 'finishedAt': now()})
                if code:
                    raise RuntimeError(f'{phase} failed ({code}); see pipeline-{phase}.log')
            manifest = json.loads((delivery.ROOT/'src/config/house-v4-manifest.json').read_text(encoding='utf-8'))
            if manifest['revision'] != REVISION:
                raise RuntimeError('Frontend revision changed before completion.')
            if args.publish_from:
                status.update(phase='publishing', updatedAt=now())
                delivery.write_json(delivery.OUT/'pipeline-status.json', status)
                status['publishedCommit'] = publish(args.publish_from)
            status.update(phase='complete', updatedAt=now())
            delivery.write_json(delivery.OUT/'pipeline-status.json', status)
        except BaseException as error:
            status.update(phase='failed', error=str(error), updatedAt=now())
            delivery.write_json(delivery.OUT/'pipeline-status.json', status)
            raise
        finally:
            if os.name == 'nt':
                ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)


if __name__ == '__main__':
    main()
