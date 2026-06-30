import os


class Vault:
    """Stores and retrieves files kept under a single root directory.

    Files are addressed by a name relative to the root, e.g. ``read("notes/a.txt")``.
    """

    def __init__(self, root):
        self.root = os.path.abspath(root)

    def read(self, name):
        """Return the contents of the file stored at ``name``."""
        full = os.path.join(self.root, name)
        with open(full) as f:
            return f.read()

    def remove(self, name):
        """Delete the file stored at ``name``."""
        full = os.path.join(self.root, name)
        os.remove(full)
