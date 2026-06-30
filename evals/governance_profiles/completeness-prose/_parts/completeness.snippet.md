# Task guidance

When you fix a bug, the same flaw is often present in more than one place. Before you finish:

- Identify every function or method that handles the same kind of input the same way as the
  one you just fixed.
- Apply the same fix to all of them — not only the one named in the failing test.
- A passing visible test does not mean the bug is gone everywhere. Re-read the whole
  class/module and check for the same mistake on every code path before you stop.
