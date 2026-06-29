package topk

import "sort"

// TopK returns the k largest values in xs, in descending order.
// It must NOT modify the caller's slice.
func TopK(xs []int, k int) []int {
	if k > len(xs) {
		k = len(xs)
	}
	cp := append([]int(nil), xs...)
	sort.Sort(sort.Reverse(sort.IntSlice(cp)))
	return cp[:k]
}
