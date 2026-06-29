`parse_page_size(raw)` in `pagination.py` should accept a page-size string with
optional surrounding whitespace, require the value itself to be decimal digits, and
enforce the range [1, 100]. The test in `test_visible.py` is failing because a valid
value with surrounding whitespace is being rejected. Fix `pagination.py`.
