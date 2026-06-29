package topk

// TopK returns the k largest values in xs, in descending order.
// It must NOT modify the caller's slice: callers rely on xs keeping its original
// contents/order after this call.
func TopK(xs []int, k int) []int {
	if k > len(xs) {
		k = len(xs)
	}
	return xs[:k] // bug: returns the first k, not the largest k
}
