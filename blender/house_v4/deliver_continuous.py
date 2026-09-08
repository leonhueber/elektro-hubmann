"""Run the full local continuous render, then verify and export its assets.

This is an explicitly started foreground runner, not a scheduled automation.
No previews, Git actions or publication occur here. Example:
  python deliver_continuous.py --blender "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" --resume
Use --plan to print the exact commands without starting Blender or writing files.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'blender'))
from house_v4.continuous_delivery import ANIMATION, OUT, REVISION, SETTINGS, now, schedule, write_json


def commands(blender, resume=False, orientation=None):
    script = ROOT / 'blender/house_v4/continuous_delivery.py'
    render = [str(blender), '-b', str(ANIMATION), '--python-exit-code', '1',
              '--python', str(script), '--', '--render']
    verify = [sys.executable, str(script), '--verify']
    export = [sys.executable, str(script), '--export']
    if resume:
        render.append('--resume')
        export.append('--resume')
    if orientation:
        export.extend(['--orientation', str(Path(orientation).resolve())])
    return [('rendering', render), ('verifying', verify), ('exporting', export)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--blender', required=True, type=Path)
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--orientation', help='Optional read-only orientation JSON source.')
    parser.add_argument('--plan', action='store_true')
    args = parser.parse_args()
    stages = commands(args.blender, args.resume, args.orientation)
    if args.plan:
        print(json.dumps({'revision': REVISION, 'frames': len(schedule()[0]), 'settings': SETTINGS,
                          'commands': [{'phase': phase, 'args': command} for phase, command in stages]}, indent=2))
        return
    if not args.blender.is_file() or not ANIMATION.is_file():
        parser.error('Blender executable and the native continuous animation must already exist.')
    try:
        from PIL import Image  # Validate the export interpreter before a long render.
    except ImportError:
        parser.error('Run this script with the configured Python runtime containing Pillow.')
    OUT.mkdir(parents=True, exist_ok=True)
    report = {'revision': REVISION, 'startedAt': now(), 'phase': 'starting', 'stages': []}
    for phase, command in stages:
        report.update(phase=phase, updatedAt=now())
        write_json(OUT / 'runner-status.json', report)
        print('CONTINUOUS_RUNNER_START', phase, flush=True)
        log_path = OUT / ('pipeline-' + phase + '.log')
        with log_path.open('a', encoding='utf-8', newline='\n') as log:
            log.write('\nRun started at ' + now() + '\n')
            log.flush()
            # Let interactive apps take priority during the long native render.
            flags = subprocess.BELOW_NORMAL_PRIORITY_CLASS if sys.platform == 'win32' else 0
            result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                                    creationflags=flags)
        report['stages'].append({'phase': phase, 'finishedAt': now(), 'exitCode': result.returncode,
                                 'log': str(log_path)})
        if result.returncode:
            report.update(phase='failed', updatedAt=now(), error='See ' + str(log_path))
            write_json(OUT / 'runner-status.json', report)
            raise SystemExit(result.returncode)
    report.update(phase='complete', updatedAt=now())
    write_json(OUT / 'runner-status.json', report)
    print('CONTINUOUS_RUNNER_COMPLETE', REVISION, flush=True)


if __name__ == '__main__':
    main()
