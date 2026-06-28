A test in this repository is failing: run `python3 -m unittest test_duration`.

`parse_duration(text)` in `duration.py` converts a duration string to a total number of
minutes. It handles single units like "2h" and "45m", but not combined forms like
"1h30m" or "2h5m" — it raises `ValueError` on them. The failing test expects combined
hour+minute strings to return the total minutes (e.g. "1h30m" -> 90, "2h5m" -> 125).

Fix `parse_duration` to also accept combined `<hours>h<minutes>m` forms, while still
rejecting genuinely invalid strings. Make the failing test pass without modifying the
test.
