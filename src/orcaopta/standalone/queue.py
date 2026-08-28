from collections import deque

class InMemoryQueue:
    def __init__(self):
        self.q = deque()

    def publish(self, event):
        self.q.append(event)

    def pop(self):
        return self.q.popleft() if self.q else None
