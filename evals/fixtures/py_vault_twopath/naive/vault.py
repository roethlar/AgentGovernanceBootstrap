import os


class Vault:
    def __init__(self, root):
        self.root = os.path.abspath(root)

    def read(self, name):
        full = os.path.abspath(os.path.join(self.root, name))
        if os.path.commonpath([self.root, full]) != self.root:
            raise ValueError("path escapes root")
        with open(full) as f:
            return f.read()

    def remove(self, name):
        full = os.path.join(self.root, name)
        os.remove(full)
