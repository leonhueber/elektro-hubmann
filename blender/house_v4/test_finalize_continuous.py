"""Finalizer guards tested without rendering, waiting or any Git mutation."""
from argparse import Namespace
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from house_v4 import finalize_continuous as finalizer

HEAD = 'a' * 40
NATIVE = 'b' * 64


class FakeGit:
    def __init__(self, root):
        self.commands = SimpleNamespace(root=Path(root))
        self.branch, self.head = 'main', HEAD
        self.staged, self.dirty = [], []
        self.remote, self.push_remote = finalizer.EXPECTED_REMOTE, finalizer.EXPECTED_REMOTE
        self.patch = b'unchanged existing foreign diff'

    def text(self, *args):
        if args == ('symbolic-ref', '--short', 'HEAD'):
            return self.branch
        if args == ('rev-parse', 'HEAD'):
            return self.head
        if args == ('remote', 'get-url', '--all', 'origin'):
            return self.remote
        if args == ('remote', 'get-url', '--push', '--all', 'origin'):
            return self.push_remote
        raise AssertionError(args)

    def names(self, *args):
        return self.staged if '--cached' in args else self.dirty

    def run(self, *args):
        if args[0] != 'diff':
            raise AssertionError('Tests must not issue Git mutations: ' + repr(args))
        return self.patch


class RemoteTipTests(unittest.TestCase):
    def test_changed_remote_is_rejected_before_ancestry_check(self):
        git = Mock()
        git.text.return_value = 'c' * 40
        with self.assertRaisesRegex(RuntimeError, 'Remote main advanced'):
            finalizer.guard_remote_tip(git, HEAD)
        git.run.assert_not_called()

    def test_pending_local_commits_must_extend_verified_remote(self):
        git = Mock()
        git.text.return_value = HEAD
        finalizer.guard_remote_tip(git, HEAD)
        git.run.assert_called_once_with('merge-base', '--is-ancestor', HEAD, 'HEAD')
        git.run.side_effect = RuntimeError('Not an ancestor')
        with self.assertRaisesRegex(RuntimeError, 'Not an ancestor'):
            finalizer.guard_remote_tip(git, HEAD)


class GuardTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.git = FakeGit(self.root)

    def test_branch_must_be_main(self):
        self.git.branch = 'codex/other-work'
        with self.assertRaisesRegex(RuntimeError, 'branch'):
            finalizer.guard(self.git, HEAD)

    def test_head_must_equal_startup_commit(self):
        self.git.head = 'c' * 40
        with self.assertRaisesRegex(RuntimeError, 'HEAD'):
            finalizer.guard(self.git, HEAD)

    def test_existing_staged_change_rejected_even_if_export_file(self):
        self.git.staged = [finalizer.CONFIG_FILES[0]]
        with self.assertRaisesRegex(RuntimeError, 'index must be empty'):
            finalizer.guard(self.git, HEAD)

    def test_existing_foreign_dirty_file_is_preserved(self):
        path = self.root / 'user-work.txt'
        path.write_text('unfinished user changes', encoding='utf-8')
        self.git.dirty = ['user-work.txt']
        baseline = finalizer.guard(self.git, HEAD)
        self.assertEqual(finalizer.guard(self.git, HEAD, baseline), baseline)
        self.assertEqual(path.read_text(), 'unfinished user changes')

    def test_new_foreign_tracked_change_rejected(self):
        baseline = finalizer.guard(self.git, HEAD)
        (self.root / 'new-change.txt').write_text('new edit')
        self.git.dirty = ['new-change.txt']
        with self.assertRaisesRegex(RuntimeError, 'new-change.txt'):
            finalizer.guard(self.git, HEAD, baseline)

    def test_modification_of_already_dirty_file_rejected(self):
        path = self.root / 'user-work.txt'
        path.write_text('initial')
        self.git.dirty = ['user-work.txt']
        baseline = finalizer.guard(self.git, HEAD)
        path.write_text('additional edit')
        with self.assertRaisesRegex(RuntimeError, 'Foreign tracked'):
            finalizer.guard(self.git, HEAD, baseline)

    def test_reverting_or_deleting_existing_dirty_file_rejected(self):
        path = self.root / 'user-work.txt'
        path.write_text('initial')
        self.git.dirty = ['user-work.txt']
        baseline = finalizer.guard(self.git, HEAD)
        path.unlink()
        with self.assertRaisesRegex(RuntimeError, 'Foreign tracked'):
            finalizer.guard(self.git, HEAD, baseline)
        self.git.dirty = []
        with self.assertRaisesRegex(RuntimeError, 'Foreign tracked'):
            finalizer.guard(self.git, HEAD, baseline)

    def test_mode_or_git_diff_change_rejected_even_with_identical_file_bytes(self):
        (self.root / 'user-work.txt').write_text('initial')
        self.git.dirty = ['user-work.txt']
        baseline = finalizer.guard(self.git, HEAD)
        self.git.patch = b'new file mode change'
        with self.assertRaisesRegex(RuntimeError, 'Foreign tracked'):
            finalizer.guard(self.git, HEAD, baseline)

    def test_only_exact_export_paths_exempt_from_foreign_guard(self):
        self.git.dirty = [*finalizer.EXPORT_PATHS, finalizer.ASSET_DIR + '/desktop/frame-0001.webp']
        self.assertEqual(finalizer.guard(self.git, HEAD, {}), {})
        self.assertFalse(finalizer.allowed_path(finalizer.ASSET_DIR + '-other/file.webp'))
        self.assertFalse(finalizer.allowed_path('src/config/house-v4-orientation.json'))
        self.assertFalse(finalizer.allowed_path(finalizer.EXPORT_REPORT + '.other'))

    def test_staged_foreign_file_blocks_commit(self):
        verified = {finalizer.CONFIG_FILES[0]}
        self.git.staged = [finalizer.CONFIG_FILES[0], 'user-work.txt']
        with self.assertRaisesRegex(RuntimeError, 'unexpected paths'):
            finalizer.guard(self.git, HEAD, {}, verified)
        self.git.staged = [finalizer.CONFIG_FILES[0]]
        self.assertEqual(finalizer.guard(self.git, HEAD, {}, verified), {})

    def test_missing_ignored_export_file_in_index_blocks_commit(self):
        image = finalizer.ASSET_DIR + '/desktop/frame-0001.webp'
        verified = {finalizer.CONFIG_FILES[0]: 'config-sha', image: 'image-sha'}
        git = Mock()
        git.names.return_value = [finalizer.CONFIG_FILES[0]]
        with self.assertRaisesRegex(RuntimeError, 'exactly all verified export files'):
            finalizer.guard_export_index(git, verified)
        git.names.assert_called_once_with('ls-files', '-z', '--',
            *[':(literal)' + path for path in finalizer.EXPORT_PATHS])
        git.names.return_value = list(verified)
        finalizer.guard_export_index(git, verified)

    def test_remote_and_push_url_are_both_pinned(self):
        finalizer.guard_remote(self.git)
        self.git.remote = 'https://github.com/other/repository.git'
        with self.assertRaisesRegex(RuntimeError, 'fetch/push URL'):
            finalizer.guard_remote(self.git)
        self.git.remote = finalizer.EXPECTED_REMOTE
        self.git.push_remote = 'https://github.com/other/repository.git'
        with self.assertRaisesRegex(RuntimeError, 'fetch/push URL'):
            finalizer.guard_remote(self.git)

    def test_additional_remote_url_is_rejected(self):
        self.git.push_remote += '\nhttps://github.com/other/repository.git'
        with self.assertRaisesRegex(RuntimeError, 'fetch/push URL'):
            finalizer.guard_remote(self.git)


class WorkflowTests(unittest.TestCase):
    def test_replaced_runner_is_rejected(self):
        current = {'revision': finalizer.REVISION, 'startedAt': 'new-run', 'phase': 'rendering'}
        with patch.object(finalizer, 'read_json', return_value=current):
            with self.assertRaisesRegex(RuntimeError, 'replaced/restarted'):
                finalizer.runner_state({'startedAt': 'original-run'}, {})

    def test_complete_runner_requires_three_successful_stages(self):
        state = {'revision': finalizer.REVISION, 'startedAt': 'run', 'phase': 'complete', 'stages': []}
        with patch.object(finalizer, 'read_json', side_effect=[state, {'identity': {}}]):
            with self.assertRaisesRegex(RuntimeError, 'three successful'):
                finalizer.runner_state({'startedAt': 'run'}, {})

    def test_site_validation_failure_never_reaches_git_mutation(self):
        args = Namespace(expected_head=HEAD, expected_native=NATIVE, timeout_hours=72, plan=False)
        git = Mock()
        git.args.side_effect = lambda *args: ['git', *args]
        checks = [('vitest', ['node', 'vitest.mjs', 'run'])]
        startup = (git, {}, {}, {'startedAt': 'run'}, checks)
        commands = Mock()
        commands.run.side_effect = RuntimeError('Vitest failed')
        with patch.object(finalizer, 'startup', return_value=startup), \
                patch.object(finalizer, 'runner_state', return_value={'phase': 'complete'}), \
                patch.object(finalizer, 'export_snapshot', return_value={}), \
                patch.object(finalizer, 'guard'), patch.object(finalizer, 'write_json'):
            with self.assertRaisesRegex(RuntimeError, 'Vitest failed'):
                finalizer.execute(args, commands, {})
        git.run.assert_not_called()

    def test_plan_does_not_wait_write_or_execute_validation(self):
        args = Namespace(expected_head=HEAD, expected_native=NATIVE, timeout_hours=72, plan=True)
        git = Mock()
        git.args.side_effect = lambda *args: ['git', *args]
        startup = (git, {}, {}, {'startedAt': 'run'}, [('vitest', ['node', 'vitest.mjs', 'run'])])
        commands = Mock()
        with patch.object(finalizer, 'startup', return_value=startup), \
                patch.object(finalizer, 'write_json') as write, \
                patch.object(finalizer.time, 'sleep') as sleep, patch('builtins.print'):
            finalizer.execute(args, commands, {})
        write.assert_not_called()
        sleep.assert_not_called()
        commands.run.assert_not_called()
        git.run.assert_not_called()


if __name__ == '__main__':
    unittest.main()
