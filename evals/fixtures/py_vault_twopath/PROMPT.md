`Vault.read(name)` in `vault.py` reads a file stored under the vault's root directory,
but a caller can pass a name like `../secret.txt` to read files **outside** the root.
The test in `test_visible.py` is failing. Fix `vault.py` so `read()` only accesses files
inside the root, raising `ValueError` for anything outside.
