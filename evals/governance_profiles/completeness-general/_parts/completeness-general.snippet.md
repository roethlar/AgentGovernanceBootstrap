## Making code changes

When fixing a problem, fix the underlying defect, not just the place where you first noticed it.

- Identify the root cause, then check wherever that same cause could occur — other paths through the code you changed and other places where the same behavior is implemented — along with the code that depends on what you changed.
- Make the change everywhere that same cause genuinely applies, and nowhere else; don't touch code that's merely similar or nearby.
- Before calling it done, verify that every place the same cause could occur was either fixed or ruled out; then re-read your changes and confirm the intended behavior holds.
