#!/usr/bin/env python3
"""4-arm governance factorial driver (sizing pilot).
Arms: none | placebo | prose | prose_hooks. Within-instance, R replicates per cell.
Injects governance via CLAUDE.md (validated keystone); captures SOURCE-ONLY diff
excluding governance + test files; instruments hook firing via a sentinel.
Usage: arms4.py <SP> <ids_file> <out_dir> <replicates> <workers>
Run from the SWE-bench_Pro-os checkout dir."""
import json, os, subprocess, sys, shlex
from concurrent.futures import ThreadPoolExecutor

SP=sys.argv[1]; IDS_FILE=sys.argv[2]; OUT=sys.argv[3]
R=int(sys.argv[4]) if len(sys.argv)>4 else 3
WORKERS=int(sys.argv[5]) if len(sys.argv)>5 else 3
MODEL=sys.argv[6] if len(sys.argv)>6 else "claude-sonnet-4-6"
MTAG="".join(MODEL.split("-")[1:3]) or "m"  # claude-sonnet-4-6 -> sonnet4 ; unique container/dir tag (no clash with running a4_ Opus pilot)
ARMS=["none","placebo","prose","prose_hooks"]
IDS=[x for x in open(IDS_FILE).read().split("\n") if x.strip()]
JSONL="helper_code/sweap_eval_full_v2.jsonl"
ROWS={json.loads(l)["instance_id"]:json.loads(l) for l in open(JSONL)}
AGENT_TIMEOUT=600
HOME=os.path.expanduser("~")
AC=SP+"/arm_content"
REAL_AGENTS=open(AC+"/real_AGENTS.md").read()
PLACEBO=open(AC+"/placebo_CLAUDE.md").read()
TRIPWIRE=open(AC+"/agents-md-tripwire.py").read()
sys.path.insert(0,"helper_code"); from image_uri import get_dockerhub_image_uri
os.makedirs(OUT+"/transcripts",exist_ok=True); os.makedirs(OUT,exist_ok=True)

def sh(c,**k): return subprocess.run(c,shell=True,text=True,capture_output=True,**k)

def test_excludes(r):
    ex=set(json.loads(r["selected_test_files_to_run"])) if isinstance(r["selected_test_files_to_run"],str) else set(r["selected_test_files_to_run"])
    last=r["before_repo_set_cmd"].strip().split("\n")[-1]
    if " -- " in last: ex.update(last.split(" -- ",1)[1].split())
    ex.update(["dump.rdb","config.json","logs"])
    # governance overlay files must NEVER reach the diff/scorer
    ex.update(["CLAUDE.md","AGENTS.md",".claude"])
    return sorted(ex)

def b64(s): import base64; return base64.b64encode(s.encode()).decode()

def inject(arm):
    """shell snippet writing arm governance into /app (run as root, pre-chown)."""
    if arm=="none": return "true"
    if arm=="placebo":
        return f"printf '%s' {shlex.quote(PLACEBO)} > /app/CLAUDE.md"
    base=(f"printf '@AGENTS.md\\n' > /app/CLAUDE.md; "
          f"printf '%s' {shlex.quote(REAL_AGENTS)} > /app/AGENTS.md")
    if arm=="prose": return base
    # prose_hooks: + project hooks + tripwire, instrumented to log firing
    settings=json.dumps({"hooks":{
        "SessionStart":[{"matcher":"compact","hooks":[{"type":"command","command":"echo reground >> /tmp/hook_fired; echo 're-read AGENTS.md'"}]}],
        "PreToolUse":[{"matcher":"Edit|Write|MultiEdit","hooks":[{"type":"command","command":"echo tripwire >> /tmp/hook_fired; python3 /app/.claude/agents-md-tripwire.py"}]}]
    }})
    return (base + "; mkdir -p /app/.claude; "
            f"printf '%s' {shlex.quote(TRIPWIRE)} > /app/.claude/agents-md-tripwire.py; "
            f"printf '%s' {shlex.quote(settings)} > /app/.claude/settings.json")

def setup_cmd(base,arm):
    return (
     "git config --global --add safe.directory /app; "
     "id agent >/dev/null 2>&1 || useradd -m -s /bin/bash agent >/dev/null 2>&1 || adduser -D agent >/dev/null 2>&1; "
     "mkdir -p /home/agent/.claude && cp /root/.claude/.credentials.json /home/agent/.claude/.credentials.json && chmod 600 /home/agent/.claude/.credentials.json; "
     "rm -f /tmp/hook_fired; "
     f"cd /app && git reset --hard {base} >/dev/null 2>&1 && git clean -fd >/dev/null 2>&1; "
     "rm -rf .git && git init -q && git add -A && git -c user.email=eval@local -c user.name=eval commit -qm base >/dev/null 2>&1 && git tag eval_base >/dev/null 2>&1; "
     + inject(arm) + "; "
     "chown -R agent /home/agent /app")

def run_cell(args):
    iid,arm,rep=args
    r=ROWS[iid]; repo=r["repo"]; base=r["base_commit"]
    img=get_dockerhub_image_uri(iid,"jefzda",repo)
    c=f"{MTAG}_{arm}_{rep}_{abs(hash(iid))%100000}"
    task=("You are fixing a bug in this repository (working directory /app). Modify ONLY non-test "
          "source code so the behavior described below is correct. Do NOT edit any files under "
          "test/ or tests/. Investigate, implement the fix, then stop.\n\n=== BUG REPORT ===\n"+r["problem_statement"])
    tf=SP+f"/task_{c}.md"; open(tf,"w").write(task)
    # connectivity-failure signatures: an empty patch caused by these is an INFRA failure
    # (e.g. proxy down), NOT a real agent no-op, and must be retried with a fresh container.
    NETERR=("ECONNREFUSED","connection refused","ENOTFOUND","fetch failed","socket hang up",
            "ETIMEDOUT","network error","Could not connect","getaddrinfo","EAI_AGAIN",
            "Connection error","502 Bad Gateway","503 Service",
            # usage-limit / quota signatures: treat an empty caused by these as INVALID, not failure
            "usage limit","hit your usage","rate limit","quota","overloaded_error","529")
    MAX_TRIES=4
    last_out=""; patch=""; hf=""; attempts=0; neterr_seen=False
    for attempt in range(1,MAX_TRIES+1):
        attempts=attempt
        sh(f"docker rm -f {c}")
        run=sh(f'docker run -d --name {c} -v "{HOME}/.local/bin/claude:/usr/local/bin/claude:ro" '
               f'-v "{HOME}/.claude/.credentials.json:/root/.claude/.credentials.json:ro" '
               f'--entrypoint sleep {shlex.quote(img)} infinity')
        if run.returncode:
            last_out="ERR_RUN: "+run.stderr[-200:];
            import time; time.sleep(5); continue
        sh(f"docker cp {tf} {c}:/tmp/agent_task.md")
        sh(f"docker exec {c} bash -lc {shlex.quote(setup_cmd(base,arm))}")
        sh(f"docker exec {c} bash -lc 'cp /tmp/agent_task.md /home/agent/task.md && chown agent /home/agent/task.md'")
        agent=sh(f"docker exec -u agent -e HOME=/home/agent -e ANTHROPIC_BASE_URL=http://10.1.10.221:8787 {c} bash -lc "
                 + shlex.quote('cd /app && timeout %d claude --model %s -p "$(cat ~/task.md)" --permission-mode bypassPermissions 2>&1'%(AGENT_TIMEOUT,MODEL)))
        last_out=(agent.stdout or "")+"\n---STDERR---\n"+(agent.stderr or "")
        ex=test_excludes(r); expathspec=" ".join("':(exclude)"+e+"'" for e in ex)
        # diff vs the pinned base TAG (not HEAD): captures the agent's net source change even
        # if it committed its work (Claude Code commits autonomously; governed arms are told to
        # "commit each slice"). git add -A stages working-tree edits + new files; --cached eval_base
        # diffs the base tree against the index, ignoring any intermediate agent commits.
        cap=sh(f"docker exec {c} bash -lc "+shlex.quote(f"cd /app && git add -A && git diff --cached eval_base -- . {expathspec}"))
        hf=sh(f"docker exec {c} bash -lc 'cat /tmp/hook_fired 2>/dev/null | sort | uniq -c | tr \"\\n\" \";\"'").stdout.strip()
        patch=cap.stdout
        neterr=any(s.lower() in last_out.lower() for s in NETERR)
        neterr_seen=neterr_seen or neterr
        if patch.strip():            # got a real patch -> done
            break
        # empty patch: retry (proxy blip or transient). Back off longer if a net error was seen.
        if attempt<MAX_TRIES:
            import time; time.sleep(20 if neterr else 8)
    open(OUT+f"/transcripts/{iid}__{arm}__r{rep}.txt","w").write(last_out)
    sh(f"docker rm -f {c}")
    nfiles=patch.count("\ndiff --git")+(1 if patch.startswith("diff --git") else 0)
    note=("" if patch.strip() else (" EMPTY/neterr" if neterr_seen else " EMPTY"))
    print(f"  {arm:11s} r{rep} {repo:20s} files={nfiles} chars={len(patch)} hooks=[{hf}] tries={attempts}{note}",flush=True)
    return {"iid":iid,"arm":arm,"rep":rep,"repo":repo,"status":"ok","patch":patch,"patch_chars":len(patch),
            "nfiles":nfiles,"hooks_fired":hf,"attempts":attempts,"neterr_seen":neterr_seen}

def preflight():
    iid0=IDS[0]; img=get_dockerhub_image_uri(iid0,"jefzda",ROWS[iid0]["repo"]); c=f"{MTAG}_preflight"
    sh(f"docker rm -f {c}")
    if sh(f'docker run -d --name {c} -v "{HOME}/.local/bin/claude:/usr/local/bin/claude:ro" -v "{HOME}/.claude/.credentials.json:/root/.claude/.credentials.json:ro" --entrypoint sleep {shlex.quote(img)} infinity').returncode: return False,"run failed"
    sh(f"docker exec {c} bash -lc {shlex.quote('id agent>/dev/null 2>&1||useradd -m agent; mkdir -p /home/agent/.claude && cp /root/.claude/.credentials.json /home/agent/.claude/.credentials.json && chmod 600 /home/agent/.claude/.credentials.json; chown -R agent /home/agent')}")
    cmd='cd /app && timeout 150 claude --model %s -p %s --permission-mode bypassPermissions 2>&1'%(MODEL,shlex.quote("Reply with exactly the word PONG and nothing else."))
    a=sh(f"docker exec -u agent -e HOME=/home/agent -e ANTHROPIC_BASE_URL=http://10.1.10.221:8787 {c} bash -lc {shlex.quote(cmd)}")
    out=(a.stdout or "")+(a.stderr or ""); sh(f"docker rm -f {c}")
    return ("PONG" in out), out[-300:]
ok,detail=preflight()
print(f"[{MODEL}] preflight PONG={ok}",flush=True)
if not ok:
    print("PREFLIGHT FAILED — aborting (model/proxy/auth?). tail:\n"+detail,flush=True); sys.exit(1)

cells=[(iid,arm,rep) for iid in IDS for arm in ARMS for rep in range(R)]
print(f"[{MODEL}] AGENT PHASE: {len(IDS)} instances x {len(ARMS)} arms x {R} reps = {len(cells)} cells, {WORKERS} workers",flush=True)
with ThreadPoolExecutor(max_workers=WORKERS) as exq:
    results=list(exq.map(run_cell,cells))
json.dump(results,open(OUT+"/arms4_model_runmeta.json","w"))

# Score per arm: build a sample jsonl + a predictions.json per (arm) with one entry per (iid,rep)
as_str=lambda v: v if isinstance(v,str) else json.dumps(v)
# sample file: one row per iid (shared); scorer keys on instance_id, so we must score per replicate separately
scores={}  # (iid,arm,rep) -> bool
for arm in ARMS:
    for rep in range(R):
        sub=[x for x in results if x["arm"]==arm and x["rep"]==rep]
        if not sub: continue
        samp=OUT+f"/arms4_sample.jsonl"
        with open(samp,"w") as f:
            for x in sub:
                r=dict(ROWS[x["iid"]]); r["fail_to_pass"]=as_str(r["FAIL_TO_PASS"]); r["pass_to_pass"]=as_str(r["PASS_TO_PASS"])
                f.write(json.dumps(r)+"\n")
        pred=[{"instance_id":x["iid"],"patch":x["patch"],"prefix":"agent"} for x in sub]
        pj=OUT+f"/arms4_pred_{arm}_r{rep}.json"; json.dump(pred,open(pj,"w"))
        od=OUT+f"/{arm}_r{rep}"; os.makedirs(od,exist_ok=True)
        sh(f"python3 swe_bench_pro_eval.py --raw_sample_path={samp} --patch_path={pj} "
           f"--output_dir={od} --scripts_dir=run_scripts --dockerhub_username=jefzda --use_local_docker --num_workers=2 --redo")
        try: rr=json.load(open(od+"/eval_results.json"))
        except Exception as e: rr={}
        # infra-empty guard: any instance the scorer dropped (no verdict) is re-scored ISOLATED
        missing=[x["iid"] for x in sub if x["iid"] not in rr]
        if missing:
            print(f"  [infra-retry] {arm} r{rep}: re-scoring {len(missing)} dropped instance(s) isolated",flush=True)
            ms=OUT+f"/arms4_resample_{arm}_r{rep}.jsonl"
            with open(ms,"w") as f:
                for x in sub:
                    if x["iid"] in missing:
                        rw=dict(ROWS[x["iid"]]); rw["fail_to_pass"]=as_str(rw["FAIL_TO_PASS"]); rw["pass_to_pass"]=as_str(rw["PASS_TO_PASS"])
                        f.write(json.dumps(rw)+"\n")
            mp=OUT+f"/arms4_repred_{arm}_r{rep}.json"
            json.dump([{"instance_id":x["iid"],"patch":x["patch"],"prefix":"agent"} for x in sub if x["iid"] in missing],open(mp,"w"))
            mod=od+"/retry"; os.makedirs(mod,exist_ok=True)
            sh(f"python3 swe_bench_pro_eval.py --raw_sample_path={ms} --patch_path={mp} "
               f"--output_dir={mod} --scripts_dir=run_scripts --dockerhub_username=jefzda --use_local_docker --num_workers=1 --redo")
            try: rr2=json.load(open(mod+"/eval_results.json"))
            except Exception: rr2={}
            rr.update(rr2)
        for iid,v in rr.items(): scores[f"{iid}|{arm}|{rep}"]=bool(v)
        still_missing=[x["iid"] for x in sub if x["iid"] not in rr]
        for iid in still_missing: scores[f"{iid}|{arm}|{rep}"]=None  # unscored, not False
# invalid-accounting: an empty patch caused by a network/quota blip is INVALID (infra),
# not an agent failure -> None. A clean empty (no neterr) stays a real failure.
for x in results:
    k=f"{x['iid']}|{x['arm']}|{x['rep']}"
    if x.get("patch_chars",0)==0 and x.get("neterr_seen"): scores[k]=None
json.dump(scores,open(OUT+"/scores.json","w"))

# Summary: per-arm resolve rate over all (iid,rep) cells
print(f"\n=== 4-ARM PILOT RESULT ({MODEL}) ===",flush=True)
from collections import defaultdict
agg=defaultdict(lambda:[0,0]); unscored=0
for k,v in scores.items():
    arm=k.split("|")[1]
    if v is None: unscored+=1; continue
    agg[arm][0]+=int(v); agg[arm][1]+=1
for arm in ARMS:
    ok,n=agg[arm]
    print(f"  {arm:11s} {ok}/{n}  ({100*ok//max(n,1)}%)",flush=True)
scored=sum(n for _,n in agg.values())
print(f"\nscored cells: {scored} / {len(cells)} run  (unscored/infra-dropped: {unscored})",flush=True)
