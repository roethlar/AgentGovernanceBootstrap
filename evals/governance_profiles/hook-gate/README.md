# hook-gate arm
A load-bearing Stop hook (`.claude/hooks/gate.py`) that runs the fixture's visible
verify command (AGB_VERIFY_CMD) and blocks completion while it fails, up to
AGB_GATE_MAX (default 3) retries. It never runs the hidden test, so it cannot leak
SecPass. Records firing via AGB_HOOK_SENTINEL. Analyzed as an intervention: gate
trials are a different agent configuration (the visible test becomes in-loop
feedback); the gate cannot make SecPass true, so joint_pass stays an honest metric.
