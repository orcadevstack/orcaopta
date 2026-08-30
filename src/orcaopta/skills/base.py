class Skill:
    name = "base"

    def execute(self, **kwargs):
        raise NotImplementedError("Skill must implement execute()")
