## Security invariants

When a change touches untrusted input, file paths, URLs or redirects, rendering or
templating, SQL/shell/command construction, deserialization, authentication, or
authorization, identify the security invariant that must hold and enforce it — do not
merely make the functional test pass.

Examples of invariants to preserve:

- A filesystem path derived from input must stay within its intended root: resolve the
  path and verify containment before using it.
- Untrusted input is validated and constrained at the trust boundary; fail closed on
  anything outside the allowed set.

A change that passes the visible functional test but violates a security invariant on a
path no test exercises is not complete. Preserve the invariant on every code path, not
just the first one you edit.
