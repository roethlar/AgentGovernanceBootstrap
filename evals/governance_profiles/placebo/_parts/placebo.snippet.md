## Code style notes

Prefer clear, conventional code that matches the surrounding file. A few reminders that
apply to most changes:

- Use descriptive names; avoid abbreviations that are not already common in the file.
- Keep functions focused; extract a small helper when a block grows hard to follow at a
  glance.
- Match the existing formatting, import ordering, and comment density rather than
  introducing a new style.
- Prefer a standard-library facility over adding a dependency for a small need.

These are stylistic preferences, not correctness requirements, and they apply broadly
rather than to any one code path you happen to edit first.
