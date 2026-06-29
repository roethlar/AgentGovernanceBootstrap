package topk

import (
	"reflect"
	"testing"
)

func TestTopKReturnsLargest(t *testing.T) {
	got := TopK([]int{3, 1, 4, 1, 5, 2}, 3)
	want := []int{5, 4, 3}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("TopK = %v, want %v", got, want)
	}
}
