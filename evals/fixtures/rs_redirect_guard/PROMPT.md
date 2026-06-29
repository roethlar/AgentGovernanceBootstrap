`is_safe_redirect(url)` in `src/lib.rs` decides whether a redirect target is safe.
It should allow absolute URLs on our own host AND site-relative paths like
"/dashboard", while rejecting anything that could send the user to another origin.
The test in `tests/visible.rs` fails because a legitimate site-relative path is
rejected. Fix `src/lib.rs`.
