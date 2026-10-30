import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "replay_events.py"
SPEC = importlib.util.spec_from_file_location("replay_events", SCRIPT)
replay = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(replay)


class ReplayGuardTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.folder = Path(self.directory.name)
        self.script_patch = patch.object(replay, "__file__", str(self.folder / SCRIPT.name))
        self.script_patch.start()
        self.addCleanup(self.script_patch.stop)
        self.events = [{"EventID": "test"} for _ in range(10)]
        self.build_patch = patch.object(replay, "build_events", return_value=self.events)
        self.build_patch.start()
        self.addCleanup(self.build_patch.stop)
        self.send_patch = patch.object(replay, "send_events")
        self.send = self.send_patch.start()
        self.addCleanup(self.send_patch.stop)

    def run_main(self, *arguments):
        output = io.StringIO()
        with patch("sys.argv", [str(SCRIPT), *arguments]), contextlib.redirect_stdout(output):
            replay.main()
        return output.getvalue()

    def test_completed_replay_is_blocked(self):
        self.assertIn("Replay complete: 10 events sent.", self.run_main())
        with self.assertRaisesRegex(SystemExit, "Replay already completed. No events sent."):
            self.run_main()
        self.assertEqual(self.send.call_count, 1)
        self.assertEqual((self.folder / ".replay-full.state").read_text().strip(), "completed")

    def test_prime_and_full_are_independent(self):
        self.assertIn("Replay complete: 1 event sent.", self.run_main("--prime"))
        self.assertEqual(len(self.send.call_args.args[0]), 1)
        self.run_main()
        self.assertEqual(len(self.send.call_args.args[0]), 10)
        with self.assertRaisesRegex(SystemExit, "Priming already completed"):
            self.run_main("--prime")
        self.assertEqual(self.send.call_count, 2)

    def test_failed_send_blocks_retry_until_explicit_override(self):
        self.send.side_effect = RuntimeError("send interrupted")
        with self.assertRaisesRegex(RuntimeError, "send interrupted"):
            self.run_main()
        with self.assertRaisesRegex(SystemExit, "previous attempt started"):
            self.run_main()
        self.assertEqual(self.send.call_count, 1)
        self.send.side_effect = None
        self.run_main("--force")
        self.assertEqual(self.send.call_count, 2)
        with self.assertRaisesRegex(SystemExit, "Replay already completed"):
            self.run_main()

    def test_force_allows_intentional_repeat(self):
        self.run_main()
        self.run_main("--force")
        self.assertEqual(self.send.call_count, 2)

    def test_dry_run_never_sends_or_creates_state(self):
        self.assertIn("Validated 10 simulated events.", self.run_main("--dry-run"))
        self.assertIn("Validated 1 simulated event.", self.run_main("--dry-run", "--prime"))
        self.send.assert_not_called()
        self.assertEqual(list(self.folder.iterdir()), [])

    def test_dry_run_ignores_completed_guard(self):
        self.run_main()
        self.run_main("--dry-run")
        self.assertEqual(self.send.call_count, 1)

    def test_existing_unfinished_reservation_blocks_another_run(self):
        (self.folder / ".replay-full.state").touch()
        with self.assertRaisesRegex(SystemExit, "previous attempt started"):
            self.run_main()
        self.send.assert_not_called()


if __name__ == "__main__":
    unittest.main()
