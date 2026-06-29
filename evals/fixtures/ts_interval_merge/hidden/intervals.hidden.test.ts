import { describe, it, expect } from "vitest";
import { mergeIntervals } from "./intervals";

describe("mergeIntervals hidden", () => {
    // This case passes on the BUGGY code (which never touches `last`, so a consumed
    // interval leaves the merged one intact) and on the correct fix, but FAILS on the
    // naive `last[1] = curr[1]` assignment, which shrinks [1,5] to [1,3].
    it("does not shrink when one interval consumes another", () => {
        expect(mergeIntervals([[1, 5], [2, 3]])).toEqual([[1, 5]]);
    });
});
