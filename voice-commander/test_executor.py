# voice-commander/test_executor.py
import unittest
from unittest.mock import MagicMock, patch
from executor import CommandExecutor


class TestCommandExecutorSecurity(unittest.TestCase):
    def setUp(self):
        self.config = {
            "static": {
                "wallpaper": "feh --bg-fill --randomize ~/Pictures/wallpapers/*",
                "lock screen": "slock",
            },
            "dynamic": {
                "project_manager_path": "/home/u/.local/bin/project_manager.sh"
            },
        }
        self.executor = CommandExecutor(self.config)
        self.payloads = [
            "$(touch /tmp/voice-commander-pwned)",
            "; touch /tmp/voice-commander-pwned",
            "&& touch /tmp/voice-commander-pwned",
        ]

    @patch("executor.subprocess.Popen")
    def test_project_start_prevents_shell_injection(self, mock_popen):
        for payload in self.payloads:
            mock_popen.reset_mock()
            self.executor.execute(f"project start {payload}")

            mock_popen.assert_called_once()
            args, kwargs = mock_popen.call_args

            # Verify shell=False
            self.assertFalse(
                kwargs.get("shell", False),
                f"Payload {payload} was executed with shell=True",
            )

            # Verify command is passed as argument list with payload isolated as a single argument
            cmd_args = args[0]
            self.assertIsInstance(cmd_args, list)
            self.assertEqual(
                cmd_args,
                ["/home/u/.local/bin/project_manager.sh", "start", payload],
            )

    @patch("executor.subprocess.Popen")
    @patch("executor.subprocess.run")
    def test_define_this_prevents_shell_injection(self, mock_run, mock_popen):
        mock_curl_res = MagicMock()
        mock_curl_res.stdout = " 1. First definition.\n 2. Second definition.\n"

        for payload in self.payloads:
            mock_run.reset_mock()
            mock_popen.reset_mock()
            mock_run.return_value = mock_curl_res

            # Enter definition state
            self.executor.execute("define this")
            self.assertTrue(self.executor.awaiting_definition_term)

            # Speak malicious term
            self.executor.execute(payload)
            self.assertFalse(self.executor.awaiting_definition_term)

            # curl is synchronous; notification launch is non-blocking.
            mock_run.assert_called_once()
            mock_popen.assert_called_once()
            curl_args, curl_kwargs = mock_run.call_args
            self.assertFalse(
                curl_kwargs.get("shell", False),
                f"curl for {payload} was executed with shell=True",
            )
            self.assertIsInstance(curl_args[0], list)
            self.assertEqual(curl_args[0], ["curl", "-s", f"dict.org/d:{payload}"])

            # Check notify-send invocation
            notify_args, notify_kwargs = mock_popen.call_args
            self.assertFalse(
                notify_kwargs.get("shell", False),
                f"notify-send for {payload} was executed with shell=True",
            )
            self.assertIsInstance(notify_args[0], list)
            self.assertEqual(
                notify_args[0],
                [
                    "notify-send",
                    f"Definition: {payload.title()}",
                    "First definition.\nSecond definition.",
                ],
            )

    @patch("executor.subprocess.Popen")
    def test_static_commands_preserve_shell_behavior(self, mock_popen):
        self.executor.execute("wallpaper")
        mock_popen.assert_called_once_with(
            "feh --bg-fill --randomize ~/Pictures/wallpapers/*",
            shell=True,
        )

    @patch("executor.subprocess.Popen")
    def test_unknown_transcript_invokes_no_subprocess(self, mock_run):
        self.executor.execute("some unknown transcript phrase")
        mock_run.assert_not_called()

    @patch("executor.subprocess.Popen")
    def test_static_command_with_prefix_or_suffix_does_not_invoke(self, mock_run):
        variations = [
            "please wallpaper",
            "wallpaper now",
            "please wallpaper now",
            "lock screen please",
            "do lock screen",
        ]
        for phrase in variations:
            mock_run.reset_mock()
            self.executor.execute(phrase)
            mock_run.assert_not_called()

    @patch("executor.subprocess.Popen")
    def test_transcript_cannot_alter_append_or_interpolate_static_command(self, mock_run):
        injection_attempts = [
            "wallpaper && rm -rf /",
            "wallpaper; reboot",
            "wallpaper | cat",
            "`reboot` wallpaper",
            "lock screen && touch /tmp/pwned",
            "lock screen; touch /tmp/pwned",
        ]
        for phrase in injection_attempts:
            mock_run.reset_mock()
            self.executor.execute(phrase)
            mock_run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
