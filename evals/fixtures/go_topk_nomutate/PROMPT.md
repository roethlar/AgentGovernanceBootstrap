`TopK(xs, k)` in `topk.go` should return the k largest values in `xs` in descending
order, and must NOT modify the caller's slice (the doc comment states this contract).
The test in `visible_test.go` fails because it returns the first k, not the largest.
Fix `topk.go`.
