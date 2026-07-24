# Governance remediation procedure (disposable session)

You were launched by `tools/refresh.py` as a **disposable** governance
remediation session in this repo. It found hygiene findings that need
judgment — they are listed in your kickoff prompt. You are not the repo's
working agent; do the remediation, commit it, and exit.

## Scope — hard boundaries

- You may touch **governance records only**: `.agents/*.md`,
  `docs/` (governance docs), and `AGENTS.md` pointers **if** the file is
  repo-owned. Refresh-installed artifacts (anything in the toolkit's
  shipped set — playbooks, skills, wrappers, shims, hooks) are
  toolkit-owned: never edit them; a wrong reference inside one is
  reported, not fixed.
- Never touch product code, tests, or anything the findings did not name.
- If a finding requires a product change or an owner decision, write it
  into `.agents/decisions.md` as an Open Decision with the evidence and
  stop there — do not implement.

## Per-finding rules

- **Dead path reference in governance prose**: the reference is wrong,
  the prose is right, or both are historical. Fix the wrong side: update
  the reference to the current path, or mark the mention historical with
  an inline `<!-- lint: allow (reason) -->` marker (this suppresses the
  same-line warning only). Never delete meaning to silence the lint.
- **Closed decision awaiting archive**: move the entry verbatim from
  `.agents/decisions.md` to `docs/history/decisions-archive.md` with a
  `> Archived <date>` pointer line, per the lifecycle rule at the top of
  decisions.md. Never summarize or drop wording.
- **Anything else**: apply the repo's own guidance (AGENTS.md, repo
  `.agents/repo-guidance.md`); when the right fix is genuinely unclear,
  record it as an Open Decision rather than guessing.

## Finish

1. Verify: the finding list is empty on a fresh look (each finding fixed
   or deliberately recorded as an Open Decision with reason).
2. Commit your changes as ONE scoped commit (`git add` of exactly the
   files you changed, never `-A`, never `-f`): message
   `governance remediation: <one-line summary>`. Push per the repo's
   `.agents/push-policy.md` (if it says `ask`, do not push — the owner
   was not present to ask).
3. Exit. Report nothing interactively; the commit is the record.
