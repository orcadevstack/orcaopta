class SkillRegistry:
    def __init__(self):
        self.skills = {}

    def register(self, name: str, cls):
        self.skills[name] = cls

    def get(self, name: str):
        return self.skills.get(name)
