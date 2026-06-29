const APP_HOST: &str = "myapp.example";

/// Returns true if `url` is a safe redirect target.
pub fn is_safe_redirect(url: &str) -> bool {
    let prefix = format!("https://{}/", APP_HOST);
    if url == format!("https://{}", APP_HOST) || url.starts_with(&prefix) {
        return true;
    }
    url.starts_with('/') && !url.starts_with("//")
}
