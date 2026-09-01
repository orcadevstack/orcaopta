from collections import deque

class ReplicationQueue:
    def __init__(self):
        self.queue = deque()

    def push(self, artifact_path):
        self.queue.append(artifact_path)

    def pop(self):
        if self.queue:
            return self.queue.popleft()
        return None
