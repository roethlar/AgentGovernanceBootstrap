The `boxes_needed(items, per_box)` function in `boxes.py` is supposed to return the
number of boxes needed to pack `items`, where each box holds up to `per_box` items
and a partly-full box still counts as one box. The test in `test_visible.py` is
failing. Fix `boxes.py` so the test passes.
