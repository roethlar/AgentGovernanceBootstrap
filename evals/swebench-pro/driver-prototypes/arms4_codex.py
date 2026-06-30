#!/usr/bin/env python3
"""4-arm governance factorial driver — CODEX subject (secondary harness).
Mirrors arms4.py (claude) but runs codex headless via its native musl binary +
subscription auth (config.toml pins gpt-5.5 via headroom; no API key). Governance
injects as AGENTS.md directly (codex reads it natively). Keeps the validated
mechanics: anti-leak re-init, capture vs pinned eval_base tag, empty-patch retry
with fresh container + neterr flag, hook-firing instrumentation.
Usage: arms4_codex.py <SP> <ids_file> <out_dir> <replicates> <workers>
Run from the SWE-bench_Pro-os checkout dir."""
import json, os, subprocess, sys, shlex, time, threading
from concurrent.futures import ThreadPoolExecutor
QUOTA_HIT=threading.Event()
QUOTA_SIGS=("hit your usage limit","usage limit","purchase more credits","quota")

SP=sys.argv[1]; IDS_FILE=sys.argv[2]; OUT=sys.argv[3]
R=int(sys.argv[4]) if len(sys.argv)>4 else 3
WORKERS=int(sys.argv[5]) if len(sys.argv)>5 else 3
ARMS=["none","placebo","prose","prose_hooks"]
IDS=[x for x in open(IDS_FILE).read().split("\n") if x.strip()]
JSONL="helper_code/sweap_eval_full_v2.jsonl"
ROWS={json.loads(l)["instance_id"]:json.loads(l) for l in open(JSONL)}
AGENT_TIMEOUT=900
HOME=os.path.expanduser("~")
AGB="/home/michael/dev/AgentGovernanceBootstrap"
AC=SP+"/arm_content"
PKG="/usr/lib/node_modules/@openai/codex"
CODEXBIN=PKG+"/node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/bin/codex"
REAL_AGENTS=open(AC+"/real_AGENTS.md").read()
PLACEBO=open(AC+"/placebo_CLAUDE.md").read()
TRIPWIRE=open(AGB+"/templates/hooks/codex/agents-md-tripwire.py").read()
sys.path.insert(0,"helper_code"); from image_uri import get_dockerhub_image_uri
TDIR=SP+"/transcripts4_codex"; os.makedirs(TDIR,exist_ok=True); os.makedirs(OUT,exist_ok=True)

def sh(c,**k): return subprocess.run(c,shell=True,text=True,capture_output=True,**k)

def test_excludes(r):
    ex=set(json.loads(r["selected_test_files_to_run"])) if isinstance(r["selected_test_files_to_run"],str) else set(r["selected_test_files_to_run"])
    last=r["before_repo_set_cmd"].strip().split("\n")[-1]
    if " -- " in last: ex.update(last.split(" -- ",1)[1].split())
    ex.update(["dump.rdb","config.json","logs","CLAUDE.md","AGENTS.md",".claude",".codex"])
    return sorted(ex)

def inject(arm):
    if arm=="none": return "true"
    if arm=="placebo": return f"printf '%s' {shlex.quote(PLACEBO)} > /app/AGENTS.md"
    base=f"printf '%s' {shlex.quote(REAL_AGENTS)} > /app/AGENTS.md"
    if arm=="prose": return base
    hooks=json.dumps({"hooks":{
        "SessionStart":[{"matcher":"compact","hooks":[{"type":"command","command":"echo reground >> /tmp/hook_fired; echo 're-read AGENTS.md'"}]}],
        "PreToolUse":[{"matcher":"apply_patch|Edit|Write","hooks":[{"type":"command","command":"echo tripwire >> /tmp/hook_fired; python3 /app/.codex/agents-md-tripwire.py"}]}]
    }})
    return (base + "; mkdir -p /app/.codex; "
            f"printf '%s' {shlex.quote(TRIPWIRE)} > /app/.codex/agents-md-tripwire.py; "
            f"printf '%s' {shlex.quote(hooks)} > /home/agent/.codex/hooks.json")

def setup_cmd(base,arm):
    return (
     "git config --global --add safe.directory /app; "
     "id agent >/dev/null 2>&1 || useradd -m -s /bin/bash agent >/dev/null 2>&1 || adduser -D agent >/dev/null 2>&1; "
     "mkdir -p /home/agent/.codex && cp /tmp/codex_auth.json /home/agent/.codex/auth.json && "
     "cp /tmp/codex_config.toml /home/agent/.codex/config.toml && chmod 600 /home/agent/.codex/auth.json; "
     "rm -f /tmp/hook_fired; "
     f"cd /app && git reset --hard {base} >/dev/null 2>&1 && git clean -fd >/dev/null 2>&1; "
     "rm -rf .git && git init -q && git add -A && git -c user.email=eval@local -c user.name=eval commit -qm base >/dev/null 2>&1 && git tag eval_base >/dev/null 2>&1; "
     + inject(arm) + "; "
     "chown -R agent /home/agent /app")

MOUNTS=(f'-v "{PKG}:{PKG}:ro" -v "{HOME}/.codex/auth.json:/tmp/codex_auth.json:ro" '
        f'-v "{HOME}/.codex/config.toml:/tmp/codex_config.toml:ro"')

def run_cell(args):
    iid,arm,rep=args
    r=ROWS[iid]; repo=r["repo"]; base=r["base_commit"]
    if QUOTA_HIT.is_set():   # codex cap already hit this window: skip without spending
        return {"iid":iid,"arm":arm,"rep":rep,"repo":repo,"status":"quota","patch":"","patch_chars":0,"nfiles":0,"hooks_fired":"","attempts":0,"neterr_seen":False,"quota":True}
    img=get_dockerhub_image_uri(iid,"jefzda",repo)
    c=f"cx_{arm}_{rep}_{abs(hash(iid))%100000}"
    task=("You are fixing a bug in this repository (working directory /app). Modify ONLY non-test "
          "source code so the behavior described below is correct. Do NOT edit any files under "
          "test/ or tests/. Investigate, implement the fix, then stop.\n\n=== BUG REPORT ===\n"+r["problem_statement"])
    tf=SP+f"/task_{c}.md"; open(tf,"w").write(task)
    NETERR=("ECONNREFUSED","connection refused","ENOTFOUND","fetch failed","socket hang up",
            "ETIMEDOUT","network error","Could not connect","getaddrinfo","EAI_AGAIN",
            "Connection error","502 Bad Gateway","503 Service","stream error","disconnected")
    MAX_TRIES=4
    last_out=""; patch=""; hf=""; attempts=0; neterr_seen=False; quota_seen=False
    agent_cmd=('cd /app && cat ~/task.md | timeout %d %s exec --dangerously-bypass-approvals-and-sandbox '
               '--dangerously-bypass-hook-trust --skip-git-repo-check -C /app 2>&1'%(AGENT_TIMEOUT,shlex.quote(CODEXBIN)))
    for attempt in range(1,MAX_TRIES+1):
        attempts=attempt
        sh(f"docker rm -f {c}")
        run=sh(f'docker run -d --name {c} {MOUNTS} --entrypoint sleep {shlex.quote(img)} infinity')
        if run.returncode:
            last_out="ERR_RUN: "+run.stderr[-200:]; time.sleep(5); continue
        sh(f"docker cp {tf} {c}:/tmp/agent_task.md")
        sh(f"docker exec {c} bash -lc {shlex.quote(setup_cmd(base,arm))}")
        sh(f"docker exec {c} bash -lc 'cp /tmp/agent_task.md /home/agent/task.md && chown agent /home/agent/task.md'")
        agent=sh(f"docker exec -u agent -e HOME=/home/agent -e CODEX_HOME=/home/agent/.codex {c} bash -lc "+shlex.quote(agent_cmd))
        last_out=(agent.stdout or "")+"\n---STDERR---\n"+(agent.stderr or "")
        ex=test_excludes(r); expathspec=" ".join("':(exclude)"+e+"'" for e in ex)
        cap=sh(f"docker exec {c} bash -lc "+shlex.quote(f"cd /app && git add -A && git diff --cached eval_base -- . {expathspec}"))
        hf=sh(f"docker exec {c} bash -lc 'cat /tmp/hook_fired 2>/dev/null | sort | uniq -c | tr \"\\n\" \";\"'").stdout.strip()
        patch=cap.stdout
        neterr=any(s.lower() in last_out.lower() for s in NETERR); neterr_seen=neterr_seen or neterr
        if any(q in last_out.lower() for q in QUOTA_SIGS):   # codex cap hit: stop the whole batch
            quota_seen=True; QUOTA_HIT.set(); break
        if patch.strip(): break
        if attempt<MAX_TRIES: time.sleep(20 if neterr else 8)
    open(TDIR+f"/{iid}__{arm}__r{rep}.txt","w").write(last_out)
    sh(f"docker rm -f {c}")
    nfiles=patch.count("\ndiff --git")+(1 if patch.startswith("diff --git") else 0)
    note=("" if patch.strip() else (" QUOTA" if quota_seen else " EMPTY/neterr" if neterr_seen else " EMPTY"))
    print(f"  {arm:11s} r{rep} {repo:20s} files={nfiles} chars={len(patch)} hooks=[{hf}] tries={attempts}{note}",flush=True)
    return {"iid":iid,"arm":arm,"rep":rep,"repo":repo,"status":("quota" if quota_seen else "ok"),"patch":patch,"patch_chars":len(patch),
            "nfiles":nfiles,"hooks_fired":hf,"attempts":attempts,"neterr_seen":neterr_seen,"quota":quota_seen}

# PREFLIGHT: one codex PONG in a throwaway container. Aborts the run (before spending
# hours) if the proxy/auth is down — catches a dead headroom proxy unattended.
def preflight():
    iid0=IDS[0]; img=get_dockerhub_image_uri(iid0,"jefzda",ROWS[iid0]["repo"]); c="cx_preflight"
    sh(f"docker rm -f {c}")
    if sh(f'docker run -d --name {c} {MOUNTS} --entrypoint sleep {shlex.quote(img)} infinity').returncode: return False,"run failed"
    sh(f"docker exec {c} bash -lc {shlex.quote('id agent>/dev/null 2>&1||useradd -m agent; mkdir -p /home/agent/.codex && cp /tmp/codex_auth.json /home/agent/.codex/auth.json && cp /tmp/codex_config.toml /home/agent/.codex/config.toml && chmod 600 /home/agent/.codex/auth.json; chown -R agent /home/agent')}")
    cmd=('echo "Reply with exactly the word PONG and nothing else." | timeout 150 %s exec --dangerously-bypass-approvals-and-sandbox --skip-git-repo-check -C /app 2>&1'%shlex.quote(CODEXBIN))
    a=sh(f"docker exec -u agent -e HOME=/home/agent -e CODEX_HOME=/home/agent/.codex {c} bash -lc {shlex.quote(cmd)}")
    out=(a.stdout or "")+(a.stderr or ""); sh(f"docker rm -f {c}")
    return ("PONG" in out), out[-300:]
ok,detail=preflight()
print(f"[CODEX] preflight PONG={ok}",flush=True)
if not ok:
    print("PREFLIGHT FAILED — aborting (proxy/auth down?). tail:\n"+detail,flush=True); sys.exit(1)

cells=[(iid,arm,rep) for iid in IDS for arm in ARMS for rep in range(R)]
print(f"[CODEX] AGENT PHASE: {len(IDS)} instances x {len(ARMS)} arms x {R} reps = {len(cells)} cells, {WORKERS} workers",flush=True)
with ThreadPoolExecutor(max_workers=WORKERS) as exq:
    results=list(exq.map(run_cell,cells))
json.dump(results,open(OUT+"/arms4_codex_runmeta.json","w"))

as_str=lambda v: v if isinstance(v,str) else json.dumps(v)
scores={}
for arm in ARMS:
    for rep in range(R):
        sub=[x for x in results if x["arm"]==arm and x["rep"]==rep]
        if not sub: continue
        samp=SP+f"/arms4cx_sample.jsonl"
        with open(samp,"w") as f:
            for x in sub:
                rw=dict(ROWS[x["iid"]]); rw["fail_to_pass"]=as_str(rw["FAIL_TO_PASS"]); rw["pass_to_pass"]=as_str(rw["PASS_TO_PASS"])
                f.write(json.dumps(rw)+"\n")
        pj=SP+f"/arms4cx_pred_{arm}_r{rep}.json"
        json.dump([{"instance_id":x["iid"],"patch":x["patch"],"prefix":"agent"} for x in sub],open(pj,"w"))
        od=OUT+f"/{arm}_r{rep}"; os.makedirs(od,exist_ok=True)
        sh(f"python3 swe_bench_pro_eval.py --raw_sample_path={samp} --patch_path={pj} "
           f"--output_dir={od} --scripts_dir=run_scripts --dockerhub_username=jefzda --use_local_docker --num_workers=2 --redo")
        try: rr=json.load(open(od+"/eval_results.json"))
        except Exception: rr={}
        missing=[x["iid"] for x in sub if x["iid"] not in rr]
        if missing:
            print(f"  [infra-retry] {arm} r{rep}: re-scoring {len(missing)} isolated",flush=True)
            ms=SP+f"/arms4cx_resample_{arm}_r{rep}.jsonl"
            with open(ms,"w") as f:
                for x in sub:
                    if x["iid"] in missing:
                        rw=dict(ROWS[x["iid"]]); rw["fail_to_pass"]=as_str(rw["FAIL_TO_PASS"]); rw["pass_to_pass"]=as_str(rw["PASS_TO_PASS"]); f.write(json.dumps(rw)+"\n")
            mp=SP+f"/arms4cx_repred_{arm}_r{rep}.json"
            json.dump([{"instance_id":x["iid"],"patch":x["patch"],"prefix":"agent"} for x in sub if x["iid"] in missing],open(mp,"w"))
            mod=od+"/retry"; os.makedirs(mod,exist_ok=True)
            sh(f"python3 swe_bench_pro_eval.py --raw_sample_path={ms} --patch_path={mp} --output_dir={mod} --scripts_dir=run_scripts --dockerhub_username=jefzda --use_local_docker --num_workers=1 --redo")
            try: rr.update(json.load(open(mod+"/eval_results.json")))
            except Exception: pass
        for iid,v in rr.items(): scores[f"{iid}|{arm}|{rep}"]=bool(v)
        for iid in [x["iid"] for x in sub if x["iid"] not in rr]: scores[f"{iid}|{arm}|{rep}"]=None
# invalid-accounting: empty patches caused by codex QUOTA or a network blip are INVALID
# (infrastructure, not agent failure) -> None. A clean empty (no quota/neterr) stays a real failure.
for x in results:
    k=f"{x['iid']}|{x['arm']}|{x['rep']}"
    if x["patch_chars"]==0 and (x.get("quota") or x.get("neterr_seen")): scores[k]=None
json.dump(scores,open(OUT+"/scores.json","w"))

from collections import defaultdict
agg=defaultdict(lambda:[0,0]); unscored=0
for k,v in scores.items():
    arm=k.split("|")[1]
    if v is None: unscored+=1; continue
    agg[arm][0]+=int(v); agg[arm][1]+=1
print("\n=== 4-ARM PILOT RESULT (CODEX gpt-5.5) ===",flush=True)
for arm in ARMS:
    ok,n=agg[arm]; print(f"  {arm:11s} {ok}/{n}  ({100*ok//max(n,1)}%)",flush=True)
scored=sum(n for _,n in agg.values())
print(f"\nscored cells: {scored} / {len(cells)}  (unscored/infra-dropped: {unscored})",flush=True)
