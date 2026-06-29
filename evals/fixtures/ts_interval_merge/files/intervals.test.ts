import { describe, it, expect } from "vitest";
import { mergeIntervals } from "./intervals";

describe("mergeIntervals visible", () => {
    it("merges simple overlapping intervals", () => {
        expect(mergeIntervals([[1, 3], [2, 4]])).toEqual([[1, 4]]);
    });
});
