# Historical Beta style reference.

class BetaJob:
    def __init__(self, config):
        self.config = config

    def run(self):
        raise NotImplementedError('Subclasses implement run()')
