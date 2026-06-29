export function mergeIntervals(intervals: [number, number][]): [number, number][] {
    if (intervals.length <= 1) return intervals;
    intervals.sort((a, b) => a[0] - b[0]);
    const result: [number, number][] = [intervals[0]];
    for (let i = 1; i < intervals.length; i++) {
        const last = result[result.length - 1];
        const curr = intervals[i];
        if (curr[0] <= last[1]) {
            last[1] = curr[1]; // naive: assigns end, shrinking when curr is consumed
        } else {
            result.push(curr);
        }
    }
    return result;
}
