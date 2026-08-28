from src.orcaopta.core.config import load_config
from src.orcaopta.standalone.mlflow_setup import configure_mlflow_standalone
from src.orcaopta.standalone.db import configure_sqlite
from src.orcaopta.standalone.queue import InMemoryQueue
from src.orcaopta.controller.self_heal import start_healing_loop

class StandaloneOrcaopta:
    def __init__(self):
        self.cfg = load_config()
        self.db = None
        self.queue = None

    def start(self):
        print("Starting Orcaopta in standalone mode...")

        # 1. MLflow standalone
        configure_mlflow_standalone(self.cfg)

        # 2. SQLite DB
        self.db = configure_sqlite(self.cfg)

        # 3. In-memory queue (Redis fallback)
        self.queue = InMemoryQueue()

        print("Standalone Orcaopta initialized.")

        # 4. Start healing loop HERE
        start_healing_loop(self.queue)

        return self
