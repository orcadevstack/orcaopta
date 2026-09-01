from .manager import ReplicationManager
import time

manager = ReplicationManager()

while True:
    manager.run()
    time.sleep(2)
