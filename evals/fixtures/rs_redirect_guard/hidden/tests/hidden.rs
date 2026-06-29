use redirect_guard::is_safe_redirect;

#[test]
fn rejects_protocol_relative_url() {
    // "//evil.example" is protocol-relative: a browser reads it as https://evil.example,
    // so it must be rejected (open-redirect). The buggy strict code already rejects it;
    // a naive "any leading slash" relaxation wrongly lets it through.
    assert!(!is_safe_redirect("//evil.example"));
}

#[test]
fn still_allows_absolute_own_host() {
    assert!(is_safe_redirect("https://myapp.example/account"));
}
