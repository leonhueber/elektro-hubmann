"""Finish one already running delivery, validate the site, commit and push exports.

Explicitly start this local process after the model/frontend commit is on main.
It does not start renders, schedule itself, retry failed Git operations, or clean
the working tree. --plan performs only startup reads and prints the exact plan.
After a failure following staging, any staged exports/local commit are preserved
for inspection; this program never resets, stashes, rebases, or force-pushes.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'blender'))
from house_v4.continuous_delivery import (ANIMATION, CHAPTERS, MANIFEST, OUT,
    REVISION, delivery_lock, identity, now, schedule, sha, write_json)

EXPECTED_REMOTE = 'https://github.com/leonhueber/elektro-hubmann.git'
ASSET_DIR = 'public/images/version-g/house-v4-continuous-r1'
CONFIG_FILES = ('src/config/house-v4-manifest.json', 'src/config/house-v4-frames.json')
EXPORT_REPORT = 'docs/version-g-qa/blender-v4-continuous-r1/frontend/export-report.json'
EXPORT_PATHS = (ASSET_DIR, *CONFIG_FILES, EXPORT_REPORT)
COMMIT_MESSAGE = 'feat: publish continuous house tour renders'
STATUS = OUT / 'finalizer-status.json'
LOG = OUT / 'finalizer.log'
RUNNER_PHASES = ('starting', 'rendering', 'verifying', 'exporting', 'complete')


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def allowed_path(path):
    return path in EXPORT_PATHS or path.startswith(ASSET_DIR + '/')


class Commands:
    """List arguments only; no shell or terminal prompts in a background run."""
    def __init__(self, root=ROOT, log=None):
        self.root, self.log = Path(root), log

    def run(self, args, timeout=600):
        args = [str(arg) for arg in args]
        if self.log:
            self.log.write('\n' + now() + ' ' + json.dumps(args) + '\n')
            self.log.flush()
        env = {**os.environ, 'GIT_TERMINAL_PROMPT': '0', 'ASTRO_TELEMETRY_DISABLED': '1', 'CI': '1'}
        result = subprocess.run(args, cwd=self.root, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, env=env,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
        if self.log:
            self.log.write(result.stdout.decode('utf-8', errors='replace'))
            self.log.write(result.stderr.decode('utf-8', errors='replace'))
            self.log.write('\nExit code: ' + str(result.returncode) + '\n')
            self.log.flush()
        if result.returncode:
            detail = result.stderr.decode('utf-8', errors='replace').strip()[-2000:]
            raise RuntimeError(f'Command failed ({result.returncode}): {args!r}\n{detail}')
        return result.stdout


class Git:
    def __init__(self, commands, executable):
        self.commands = commands
        self.prefix = [str(executable), '-c', 'safe.directory=' + commands.root.as_posix()]

    def args(self, *args):
        return [*self.prefix, *args]

    def run(self, *args):
        return self.commands.run(self.args(*args))

    def text(self, *args):
        return self.run(*args).decode('utf-8', errors='strict').strip()

    def names(self, *args):
        return [name.decode('utf-8', errors='strict') for name in self.run(*args).split(b'\0') if name]


def index_paths(git):
    return git.names('diff', '--cached', '--no-ext-diff', '--no-textconv',
                     '--name-only', '--no-renames', '-z', '--')


def guard_export_index(git, verified):
    indexed = set(git.names('ls-files', '-z', '--',
        *[':(literal)' + path for path in EXPORT_PATHS]))
    if indexed != set(verified):
        raise RuntimeError('Git index does not contain exactly all verified export files.')


def foreign_snapshot(git):
    """Preserve existing dirty files, and detect later edits to those same files."""
    names = git.names('diff', '--no-ext-diff', '--no-textconv', '--name-only',
                     '--no-renames', '-z', 'HEAD', '--')
    result = {}
    for name in names:
        if allowed_path(name):
            continue
        path = git.commands.root / name
        if path.is_symlink():
            content = {'symlink': os.readlink(path)}
        elif path.is_file():
            content = {'sha256': sha(path)}
        elif path.is_dir():
            # Submodule changes (including dirty state) are present in this diff.
            patch = git.run('diff', '--no-ext-diff', '--no-textconv', 'HEAD', '--', ':(literal)' + name)
            content = {'directoryDiffSha256': hashlib.sha256(patch).hexdigest()}
        else:
            content = {'deleted': True}
        patch = git.run('diff', '--no-ext-diff', '--no-textconv', '--no-color',
                        '--binary', '--no-renames', 'HEAD', '--', ':(literal)' + name)
        content['gitDiffSha256'] = hashlib.sha256(patch).hexdigest()
        result[name] = content
    return result


def guard(git, expected_head, baseline=None, staged_files=None):
    if git.text('symbolic-ref', '--short', 'HEAD') != 'main':
        raise RuntimeError('Git branch must remain main.')
    if git.text('rev-parse', 'HEAD') != expected_head:
        raise RuntimeError('Git HEAD differs from the expected commit; no automatic reconciliation.')
    staged = set(index_paths(git))
    if staged_files is None and staged:
        raise RuntimeError('Git index must be empty.')
    if staged_files is not None and (not staged or not staged.issubset(staged_files)):
        raise RuntimeError('Git index contains unexpected paths or no export changes.')
    current = foreign_snapshot(git)
    if baseline is not None and current != baseline:
        changed = sorted(name for name in set(current) | set(baseline)
                         if current.get(name) != baseline.get(name))
        raise RuntimeError('Foreign tracked working-tree changes since startup: ' + ', '.join(changed))
    return current


def guard_remote(git):
    # --get-url expands insteadOf/pushInsteadOf; check every configured URL.
    for args in [('remote', 'get-url', '--all', 'origin'),
                 ('remote', 'get-url', '--push', '--all', 'origin')]:
        if git.text(*args).splitlines() != [EXPECTED_REMOTE]:
            raise RuntimeError('origin fetch/push URL must equal ' + EXPECTED_REMOTE)


def cli_path(package, name):
    folder = ROOT / 'node_modules' / package
    metadata = read_json(folder / 'package.json')
    bins = metadata.get('bin', {})
    relative = bins if isinstance(bins, str) else bins[name]
    result = (folder / relative).resolve()
    if not result.is_file():
        raise RuntimeError('Missing installed Node CLI: ' + str(result))
    return result


def validation_commands(node):
    return [
        ('vitest', [str(node), str(cli_path('vitest', 'vitest')), 'run']),
        ('astro_check', [str(node), str(cli_path('astro', 'astro')), 'check']),
        ('astro_build', [str(node), str(cli_path('astro', 'astro')), 'build']),
    ]


def runner_state(reference=None, expected_identity=None):
    value = read_json(OUT / 'runner-status.json')
    if value.get('revision') != REVISION or not value.get('startedAt'):
        raise RuntimeError('Runner revision/start timestamp is invalid.')
    if reference is not None and value['startedAt'] != reference['startedAt']:
        raise RuntimeError('Runner was replaced/restarted after finalizer startup.')
    if value.get('phase') == 'failed':
        raise RuntimeError('Delivery runner failed: ' + str(value.get('error', 'see runner logs')))
    if value.get('phase') not in RUNNER_PHASES:
        raise RuntimeError('Unexpected delivery runner phase: ' + str(value.get('phase')))
    progress = read_json(OUT / 'render-progress.json')
    if expected_identity is not None and progress.get('identity') != expected_identity:
        raise RuntimeError('Runner render identity does not match the expected native source/settings.')
    if value['phase'] == 'complete':
        stages = value.get('stages', [])
        if [stage.get('phase') for stage in stages] != ['rendering', 'verifying', 'exporting'] or any(
                stage.get('exitCode') != 0 for stage in stages):
            raise RuntimeError('Complete runner lacks three successful delivery stages.')
    return value


def export_snapshot(expected_native, expected_identity):
    """Recheck provenance and every published byte before committing its allowlist."""
    if sha(ANIMATION) != expected_native:
        raise RuntimeError('Native source SHA changed.')
    progress = read_json(OUT / 'render-progress.json')
    if progress.get('identity') != expected_identity:
        raise RuntimeError('Export render identity changed.')
    pipeline = read_json(OUT / 'pipeline-status.json')
    frames, aliases = schedule()
    if (pipeline.get('phase') != 'complete' or pipeline.get('activated') is not True
            or pipeline.get('revision') != REVISION
            or pipeline.get('nativeAnimationSha256') != expected_native
            or pipeline.get('completedFrames') != len(frames)):
        raise RuntimeError('Production export is not complete and activated for the expected native SHA.')
    manifest = read_json(ROOT / CONFIG_FILES[0])
    if manifest != MANIFEST or manifest.get('revision') != 'v4-continuous-01':
        raise RuntimeError('Active manifest differs from the expected continuous revision/profile.')
    if read_json(ROOT / CONFIG_FILES[1]) != {profile: aliases for profile in MANIFEST['profiles']}:
        raise RuntimeError('Active frame mapping differs from the continuous schedule.')
    report = read_json(ROOT / EXPORT_REPORT)
    if (report.get('revision') != REVISION or report.get('nativeAnimationSha256') != expected_native
            or report.get('settings') != expected_identity['settings']
            or report.get('nativeFrames') != len(frames) or not report.get('validatedAt')
            or set(report.get('profiles', {})) != set(MANIFEST['profiles'])):
        raise RuntimeError('Export report does not prove this native source/profile.')
    names = {f'frame-{frame:04d}.webp' for frame in frames} | {c['id'] + '.webp' for c in CHAPTERS}
    result = {}
    for name in (*CONFIG_FILES, EXPORT_REPORT):
        path = ROOT / name
        if path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()):
            raise RuntimeError('Export metadata must be a regular project file: ' + name)
        result[name] = sha(path)
    for profile, dimensions in MANIFEST['profiles'].items():
        details = report['profiles'][profile]
        if (details.get('width'), details.get('height')) != (dimensions['width'], dimensions['height']):
            raise RuntimeError('Export dimensions mismatch: ' + profile)
        hashes = details.get('sha256', {})
        if set(hashes) != names:
            raise RuntimeError('Export report has missing or extra frame/poster names: ' + profile)
        for name, expected_sha in hashes.items():
            relative = ASSET_DIR + '/' + profile + '/' + name
            path = ROOT / relative
            if (path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve())
                    or not path.is_file() or sha(path) != expected_sha):
                raise RuntimeError('Exported asset missing, linked or changed: ' + relative)
            result[relative] = expected_sha
    actual = {path.relative_to(ROOT).as_posix() for path in (ROOT / ASSET_DIR).rglob('*') if path.is_file()}
    if actual != {name for name in result if name.startswith(ASSET_DIR + '/')}:
        raise RuntimeError('Export folder contains unexpected files; refusing to stage the directory.')
    return result


def startup(args, commands):
    if not re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', args.expected_head):
        raise RuntimeError('--expected-head must be a full lowercase Git commit SHA.')
    if not re.fullmatch(r'[0-9a-f]{64}', args.expected_native):
        raise RuntimeError('--expected-native must be a full lowercase SHA-256.')
    if not 0 < args.timeout_hours <= 72:
        raise RuntimeError('Wait timeout must be greater than zero and at most 72 hours.')
    git_executable = shutil.which('git')
    node = Path(args.node or shutil.which('node') or '')
    if not git_executable or not node.is_file():
        raise RuntimeError('Installed Git and Node executables are required.')
    git = Git(commands, git_executable)
    if Path(git.text('rev-parse', '--show-toplevel')).resolve() != ROOT.resolve():
        raise RuntimeError('Git working tree is not the expected project directory.')
    baseline = guard(git, args.expected_head)
    guard_remote(git)
    version = commands.run([node, '--version']).decode().strip()
    if not version.startswith('v24.'):
        raise RuntimeError('This project requires Node 24; found ' + version)
    checks = validation_commands(node)
    expected_identity = identity()
    if expected_identity['nativeAnimationSha256'] != args.expected_native:
        raise RuntimeError('Native source SHA does not match --expected-native.')
    reference = runner_state(expected_identity=expected_identity)
    return git, baseline, expected_identity, reference, checks


def execute(args, commands, report):
    git, baseline, expected_identity, reference, checks = startup(args, commands)
    staged_args = ['add', '--', *[':(literal)' + path for path in EXPORT_PATHS]]
    plan = {'revision': REVISION, 'expectedHead': args.expected_head,
        'expectedNativeSha256': args.expected_native, 'expectedRemote': EXPECTED_REMOTE,
        'runnerStartedAt': reference['startedAt'], 'timeoutHours': args.timeout_hours,
        'existingForeignTrackedChanges': baseline, 'exportPaths': EXPORT_PATHS,
        'validationCommands': [{'phase': name, 'args': command} for name, command in checks],
        'gitCommands': [git.args('fetch', '--no-tags', 'origin', 'main'), git.args(*staged_args),
            git.args('commit', '-m', COMMIT_MESSAGE), git.args('push', 'origin', 'HEAD:main')],
        'statusPath': str(STATUS), 'logPath': str(LOG), 'automaticRetry': False}
    if args.plan:
        print(json.dumps(plan, indent=2))
        return
    report.update(plan)

    def phase(name, **extra):
        report.update(phase=name, updatedAt=now(), **extra)
        write_json(STATUS, report)

    deadline = time.monotonic() + args.timeout_hours * 3600
    while True:
        runner = runner_state(reference, expected_identity)
        if runner['phase'] == 'complete':
            break
        if time.monotonic() >= deadline:
            raise RuntimeError('Delivery runner did not complete within the configured wait timeout.')
        phase('waiting', runnerPhase=runner['phase'])
        time.sleep(min(30, max(0, deadline - time.monotonic())))
    phase('validating_export')
    verified = export_snapshot(args.expected_native, expected_identity)
    guard(git, args.expected_head, baseline)
    for name, command in checks:
        phase(name)
        commands.run(command, timeout=3600)
        report.setdefault('checks', []).append({'name': name, 'completedAt': now(), 'exitCode': 0})

    def unchanged_exports():
        runner_state(reference, expected_identity)
        if export_snapshot(args.expected_native, expected_identity) != verified:
            raise RuntimeError('Export files changed after validation.')

    unchanged_exports()
    guard(git, args.expected_head, baseline)
    guard_remote(git)
    phase('fetching')
    git.run('fetch', '--no-tags', 'origin', 'main')
    if git.text('rev-parse', 'FETCH_HEAD') != args.expected_head:
        raise RuntimeError('Remote main advanced or diverged; refusing automatic integration.')
    unchanged_exports()
    guard(git, args.expected_head, baseline)
    phase('staging', indexMayContainExports=True)
    git.run(*staged_args)
    unchanged_exports()
    guard(git, args.expected_head, baseline, set(verified))
    guard_export_index(git, verified)
    if git.names('diff', '--no-ext-diff', '--no-textconv', '--name-only', '-z', '--',
                 *[':(literal)' + path for path in EXPORT_PATHS]):
        raise RuntimeError('Staged export bytes differ from the validated working tree.')
    phase('committing')
    git.run('commit', '-m', COMMIT_MESSAGE)
    commit = git.text('rev-parse', 'HEAD')
    report.update(commit=commit, indexMayContainExports=False)
    if git.text('rev-parse', 'HEAD^') != args.expected_head:
        raise RuntimeError('Export commit has an unexpected parent.')
    committed = set(git.names('diff-tree', '--no-commit-id', '--name-only', '--no-renames', '-r', '-z', commit))
    if not committed or not committed.issubset(verified):
        raise RuntimeError('Export commit contains unexpected paths.')
    unchanged_exports()
    guard(git, commit, baseline)
    guard_remote(git)
    phase('pushing')
    git.run('push', 'origin', 'HEAD:main')
    phase('complete', pushed=True, finishedAt=now())


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--expected-head', required=True)
    parser.add_argument('--expected-native', required=True)
    parser.add_argument('--node', type=Path, help='Installed Node 24 executable; defaults to PATH.')
    parser.add_argument('--timeout-hours', type=float, default=72)
    parser.add_argument('--plan', action='store_true')
    args = parser.parse_args(argv)
    report = {'revision': REVISION, 'startedAt': now(), 'phase': 'starting', 'pushed': False,
        'expectedHead': args.expected_head, 'expectedNativeSha256': args.expected_native}
    if args.plan:
        execute(args, Commands(), report)
        return
    # Separate lock: never hold the render/export runner's delivery lock.
    with delivery_lock(OUT / 'finalizer-state'):
        with LOG.open('a', encoding='utf-8', newline='\n') as log:
            write_json(STATUS, report)
            try:
                execute(args, Commands(log=log), report)
            except Exception as exc:
                report.update(phase='failed', updatedAt=now(), error=str(exc))
                write_json(STATUS, report)
                log.write('\nFINALIZER_FAILED: ' + str(exc) + '\n')
                print('CONTINUOUS_FINALIZER_FAILED', str(exc), file=sys.stderr, flush=True)
                raise SystemExit(1)
    print('CONTINUOUS_FINALIZER_COMPLETE', report['commit'], flush=True)


if __name__ == '__main__':
    main()
