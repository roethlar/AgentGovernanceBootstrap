A test in this repository is failing (run the Pester suite under `tests/`).

The token compressor's `minimal` level applies a generic comment stripper that removes
lines beginning with `#`. This is too aggressive: when a `#` line appears *inside* a
multi-line string (e.g. a Python triple-quoted string), it is part of the string's data,
not a comment, and must not be removed. The failing test feeds `Invoke-PtcRead` a file
whose multi-line string contains a `# comment inside string` line and asserts that line
survives at `minimal` level.

Fix the compressor so the `minimal` level does not strip `#` lines that are inside
multi-line strings, while still stripping real comments. Make the failing test pass
without modifying the test.
