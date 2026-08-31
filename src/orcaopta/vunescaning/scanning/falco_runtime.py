import subprocess
import json
import threading
import queue
from typing import Dict, Any, List


class FalcoRuntime:
    """
    Full Falco runtime engine for Orcaopta.
    Supports:
    - Starting Falco in JSON output mode
    - Streaming events asynchronously
    - Applying custom rules
    - Health checks
    - Graceful shutdown
    """

    def __init__(self):
        self.process = None
        self.event_queue = queue.Queue()
        self.running = False

    # -------------------------------------------------------------
    # Start Falco in JSON mode
    # -------------------------------------------------------------
    def start(self):
        """
        Starts Falco with JSON output so Orcaopta can parse events.
        """
        cmd = [
            "falco",
            "--json",
            "--disable-cri-api",
            "--disable-k8s-api",
        ]

        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        self.running = True

        # Start background thread to read events
        threading.Thread(target=self._stream_events, daemon=True).start()

        return True

    # -------------------------------------------------------------
    # Internal: stream Falco events
    # -------------------------------------------------------------
    def _stream_events(self):
        """
        Reads Falco events line-by-line and pushes them into a queue.
        """
        while self.running and self.process and self.process.stdout:
            line = self.process.stdout.readline()
            if not line:
                continue

            try:
                event = json.loads(line)
                self.event_queue.put(event)
            except json.JSONDecodeError:
                continue

    # -------------------------------------------------------------
    # Get next Falco event
    # -------------------------------------------------------------
    def next_event(self) -> Dict[str, Any]:
        """
        Returns the next Falco event from the queue.
        Non-blocking.
        """
        try:
            return self.event_queue.get_nowait()
        except queue.Empty:
            return None

    # -------------------------------------------------------------
    # Apply custom Falco rules
    # -------------------------------------------------------------
    def apply_rules(self, rules_file: str):
        """
        Installs custom Falco rules using falcoctl.
        """
        cmd = ["falcoctl", "rules", "install", rules_file]
        return subprocess.run(cmd, capture_output=True, text=True)

    # -------------------------------------------------------------
    # Load rules from local file
    # -------------------------------------------------------------
    def load_local_rules(self, rules_file: str):
        """
        Load rules directly into Falco (local rules file).
        """
        cmd = ["falco", "-r", rules_file]
        return subprocess.run(cmd, capture_output=True, text=True)

    # -------------------------------------------------------------
    # Health check
    # -------------------------------------------------------------
    def health(self) -> bool:
        """
        Checks if Falco is running.
        """
        return self.process is not None and self.process.poll() is None

    # -------------------------------------------------------------
    # Stop Falco
    # -------------------------------------------------------------
    def stop(self):
        """
        Gracefully stops Falco.
        """
        self.running = False
        if self.process:
            self.process.terminate()
            self.process.wait()
        return True

    # -------------------------------------------------------------
    # Convert Falco event → Orcaopta Issue
    # -------------------------------------------------------------
    def convert_event_to_issue(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converts Falco JSON event into Orcaopta Issue format.
        """

        if not event:
            return None

        return {
            "id": event.get("rule", "FALCO-RUNTIME"),
            "title": event.get("output", "Falco runtime event"),
            "severity": event.get("priority", "unknown"),
            "description": event.get("output", ""),
            "source": "runtime",
            "metadata": event
        }

    # -------------------------------------------------------------
    # Collect all events as issues
    # -------------------------------------------------------------
    def collect_issues(self) -> List[Dict[str, Any]]:
        issues = []
        while True:
            event = self.next_event()
            if not event:
                break
            issue = self.convert_event_to_issue(event)
            if issue:
                issues.append(issue)
        return issues
