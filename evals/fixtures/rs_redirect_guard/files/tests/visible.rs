use redirect_guard::is_safe_redirect;

#[test]
fn allows_site_relative_path() {
    // "/dashboard" stays on our origin and must be accepted.
    assert!(is_safe_redirect("/dashboard"));
}
