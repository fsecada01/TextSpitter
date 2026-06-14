use chardetng::EncodingDetector;
use pyo3::prelude::*;

/// Map a WHATWG encoding label to a Python codec name.
fn to_python_codec(whatwg_name: &str) -> String {
    match whatwg_name {
        "UTF-8" => "utf-8".into(),
        "UTF-16LE" => "utf-16-le".into(),
        "UTF-16BE" => "utf-16-be".into(),
        // chardetng collapses ISO-8859-1 and windows-1252 into windows-1252;
        // Python's canonical name for that codec is cp1252.
        "windows-1252" | "ISO-8859-1" => "cp1252".into(),
        other => other.to_lowercase(),
    }
}

/// Detect the character encoding of raw bytes.
///
/// Uses chardetng for a single-pass, high-accuracy detection.
/// Returns a Python codec name suitable for use with ``bytes.decode()``.
/// Falls back to ``"utf-8"`` if detection is inconclusive.
#[pyfunction]
pub fn detect_encoding(data: &[u8]) -> String {
    if data.is_empty() {
        return "utf-8".into();
    }

    // Feed the entire buffer; last=true signals end-of-stream.
    let mut detector = EncodingDetector::new();
    detector.feed(data, true);

    // guess(tld, allow_utf8): None TLD, allow UTF-8 as a candidate.
    let encoding = detector.guess(None, true);
    to_python_codec(encoding.name())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn detects_utf8() {
        let data = "Hello, world! — Unicode café".as_bytes();
        assert_eq!(detect_encoding(data), "utf-8");
    }

    #[test]
    fn detects_windows1252() {
        // 0x93/0x94 are Windows-1252 "smart quotes", invalid in UTF-8.
        let data = b"Hello \x93world\x94";
        let enc = detect_encoding(data);
        assert!(enc == "cp1252" || enc == "windows-1252", "got: {enc}");
    }

    #[test]
    fn empty_bytes_returns_utf8() {
        assert_eq!(detect_encoding(b""), "utf-8");
    }
}
