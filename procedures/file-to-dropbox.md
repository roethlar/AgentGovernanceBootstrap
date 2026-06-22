# Writing a File to the agent-harvest Dropbox (shared transport)

The canonical mechanics for writing one file to the shared `agent-harvest`
dropbox. Both submission paths use it — harvest reports
(`procedures/migration.md` Step 8) and bug reports
(`procedures/file-bug-report.md`) — so the transport lives in exactly one place.
Callers supply only the **destination path within the dropbox** (a top-level
filename for harvest reports, or `bugs/<filename>` for bug reports), and an
**in-repo fallback path**; everything below is identical for both. Below,
`<dest>` is that dropbox-relative path.

The dropbox is `agent-harvest`, canonical on GitHub at `roethlar/agent-harvest`,
default branch `main`. Its local clone path, if any, is in this repo's untracked
`harvest.config.json` (`harvestRepoPath`).

## Invariants for every write

- **Append-only.** Never overwrite or edit a file that already exists in the
  dropbox. On a name collision, append `-2` (then `-3`, …) to the filename.
- **Writing the local file is automatic; publishing is gated.** Drafting the file
  is not a publish. Sending it to the dropbox — whether by a direct `gh api`
  write to GitHub or by a clone push — publishes it and requires an explicit
  owner go. Ask once, in one line, before the publishing step, naming the remote.

## Preferred — no clone, via `gh`

If `gh` is installed and authenticated (`gh auth status`), write straight to
GitHub without a local clone. This commits directly to `main`, so it IS the
publish — get the owner's go first, then:

```
gh api -X PUT repos/roethlar/agent-harvest/contents/<dest> \
  -f message="<one-line commit message>" \
  -f branch=main \
  -f content="$(base64 -i <local-file>)"
```

(`content` must be base64: `base64 -i` on macOS, `base64 -w0` on GNU.) If the PUT
fails because the path already exists, rename per the append-only rule and retry.

**Verify against the commit, not a re-read of the path.** The contents API can
serve a briefly stale read-after-write, so confirm success from the PUT response
(`.commit.sha`, `.content.sha`) or by checking the tip of `main`
(`gh api repos/roethlar/agent-harvest/commits/main`) — not by immediately
re-GETting the file path.

## Fallback — local clone

If `gh` is unavailable or unauthed: ensure a local clone of the dropbox. Use
`harvestRepoPath` if it is set and on disk; otherwise clone
`https://github.com/roethlar/agent-harvest.git` to a path the owner names (or
`~/dev/agent-harvest`). Before reading or writing, sync fast-forward-only the way
the harvest sweep does (`git -C <clone> ls-remote --exit-code <remote> HEAD`,
then `fetch` and `merge --ff-only`) so you are not writing onto a stale tree.
Write the file at `<dest>`, then — with the owner's go — commit and push
the dropbox repo only, naming the remote in the one-line ask. If the push fails,
say so plainly and leave the committed file in place.

## Last resort — dropbox unreachable

If the dropbox cannot be reached (offline, no clone possible, no `gh`), write the
file to the caller's in-repo fallback path so it travels with the current repo's
git, and say plainly that it landed there instead of the shared dropbox.
