package topk

import (
	"reflect"
	"testing"
)

func TestTopKDoesNotMutateInput(t *testing.T) {
	xs := []int{3, 1, 4, 1, 5, 2}
	original := append([]int(nil), xs...)
	_ = TopK(xs, 3)
	if !reflect.DeepEqual(xs, original) {
		t.Fatalf("TopK mutated caller's slice: got %v, want %v", xs, original)
	}
}
