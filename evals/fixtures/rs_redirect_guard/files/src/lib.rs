const APP_HOST: &str = "myapp.example";

/// Returns true if `url` is a safe redirect target.
///
/// Allowed: absolute URLs on our own host (https://myapp.example/...) and
/// site-relative paths (e.g. "/dashboard"). Anything that could send the user to
/// another origin MUST be rejected (open-redirect).
pub fn is_safe_redirect(url: &str) -> bool {
    let prefix = format!("https://{}/", APP_HOST);
    // bug: only the absolute-host form is allowed; legitimate site-relative paths
    // like "/dashboard" are wrongly rejected.
    url == format!("https://{}", APP_HOST) || url.starts_with(&prefix)
}
