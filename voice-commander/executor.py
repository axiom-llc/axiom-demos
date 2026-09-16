# voice-commander/executor.py
"""Handles matching text to commands and executing them."""
import re
import subprocess
import sys

class CommandExecutor:
    """Matches text to commands and executes them."""

    def __init__(self, commands_config: dict):
        self.static_commands = commands_config.get("static", {})
        self.dynamic_config = commands_config.get("dynamic", {})
        self.awaiting_definition_term = False

    def _run_shell_command(self, command: str, is_dynamic: bool = False, term: str = ""):
        prefix = "DYNAMIC" if is_dynamic else "STATIC"
        log_term = f"'{term}'" if term else ""
        print(f"==> EXECUTING {prefix}: {command} {log_term}", file=sys.stderr)
        subprocess.Popen(command, shell=True)

    def _run_command(self, cmd: list, is_dynamic: bool = False, term: str = ""):
        prefix = "DYNAMIC" if is_dynamic else "STATIC"
        log_term = f"'{term}'" if term else ""
        cmd_str = " ".join(cmd)
        print(f"==> EXECUTING {prefix}: {cmd_str} {log_term}".rstrip(), file=sys.stderr)
        subprocess.Popen(cmd, shell=False)

    def execute(self, text: str) -> None:
        """The main execution logic for a piece of transcribed text."""
        print(f"Heard: '{text}'", file=sys.stderr)

        # 1. Handle stateful commands first
        if self.awaiting_definition_term:
            curl_res = subprocess.run(
                ["curl", "-s", f"dict.org/d:{text}"],
                capture_output=True,
                text=True,
                shell=False,
            )
            stdout = curl_res.stdout if isinstance(curl_res.stdout, str) else ""
            lines = []
            for line in stdout.splitlines():
                if re.match(r"^ [1-9].", line):
                    lines.append(re.sub(r"^[ ]*[0-9.]* ", "", line))
                    if len(lines) == 3:
                        break
            definition = "\n".join(lines)
            self._run_command(
                ["notify-send", f"Definition: {text.title()}", definition],
                is_dynamic=True,
                term=text,
            )
            self.awaiting_definition_term = False
            return

        if text == "define this":
            print(">>> Ready to define. Speak the term now.", file=sys.stderr)
            self.awaiting_definition_term = True
            return

        # 2. Handle static commands
        if text in self.static_commands:
            if text == "stop listening":
                print("Exit command received. Shutting down.", file=sys.stderr)
                sys.exit(0)
            self._run_shell_command(self.static_commands[text])
            return

        # 3. Handle dynamic commands with patterns
        words = text.split()
        pm_path = self.dynamic_config.get("project_manager_path")
        if pm_path and len(words) > 2 and words[0] == "project" and words[1] == "start":
            project_name = " ".join(words[2:])
            self._run_command(
                [pm_path, "start", project_name],
                is_dynamic=True,
                term=project_name,
            )
            return
        
        if pm_path and text == "project stop":
            self._run_shell_command(f"{pm_path} stop")
            return

        # 4. If no match was found
        print("--> (No command matched)", file=sys.stderr)
