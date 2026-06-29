package topk

import "sort"

// TopK returns the k largest values in xs, in descending order.
func TopK(xs []int, k int) []int {
	if k > len(xs) {
		k = len(xs)
	}
	sort.Sort(sort.Reverse(sort.IntSlice(xs))) // naive: mutates the caller's slice
	return xs[:k]
}
