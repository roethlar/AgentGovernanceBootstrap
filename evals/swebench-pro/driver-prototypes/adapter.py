#!/usr/bin/env python3
"""P1-seed adapter: jsonl instances -> (sample.jsonl, gold predictions.json).
Encodes the two CSV-vs-jsonl gotchas found in P0:
  (1) scorer reads lowercase fail_to_pass/pass_to_pass; jsonl has uppercase -> alias
  (2) scorer eval()s those fields expecting str; jsonl FAIL_TO_PASS is a list,
      PASS_TO_PASS is a str -> coerce both to string form (survives pandas read_json)
"""
import json, sys
JSONL="helper_code/sweap_eval_full_v2.jsonl"
as_str=lambda v: v if isinstance(v,str) else json.dumps(v)
def adapt(inst):
    inst=dict(inst)
    inst['fail_to_pass']=as_str(inst['FAIL_TO_PASS'])
    inst['pass_to_pass']=as_str(inst['PASS_TO_PASS'])
    return inst
def main(out_sample, out_gold, instance_ids):
    rows={json.loads(l)['instance_id']:json.loads(l) for l in open(JSONL)}
    with open(out_sample,"w") as f:
        for iid in instance_ids: f.write(json.dumps(adapt(rows[iid]))+"\n")
    gold=[{"instance_id":iid,"patch":rows[iid]['patch'],"prefix":"gold"} for iid in instance_ids]
    json.dump(gold, open(out_gold,"w"))
if __name__=="__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
