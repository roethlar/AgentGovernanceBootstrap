import os


class Vault:
    def __init__(self, root):
        self.root = os.path.abspath(root)

    def _resolve(self, name):
        full = os.path.abspath(os.path.join(self.root, name))
        if os.path.commonpath([self.root, full]) != self.root:
            raise ValueError("path escapes root")
        return full

    def read(self, name):
        with open(self._resolve(name)) as f:
            return f.read()

    def remove(self, name):
        os.remove(self._resolve(name))
