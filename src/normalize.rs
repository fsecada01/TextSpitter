use pyo3::prelude::*;
use rayon::prelude::*;
use unicode_normalization::UnicodeNormalization;

#[pyclass]
pub struct TextNormalizer {
    unicode_form: String,
    collapse_whitespace: bool,
    repair_ocr: bool,
    strip_headers_footers: bool,
}

#[pymethods]
impl TextNormalizer {
    #[new]
    #[pyo3(signature = (
        unicode_form = "NFC".to_string(),
        collapse_whitespace = true,
        repair_ocr = false,
        strip_headers_footers = false,
    ))]
    pub fn new(
        unicode_form: String,
        collapse_whitespace: bool,
        repair_ocr: bool,
        strip_headers_footers: bool,
    ) -> Self {
        Self { unicode_form, collapse_whitespace, repair_ocr, strip_headers_footers }
    }

    pub fn normalize(&self, text: &str) -> String {
        self.normalize_one(text)
    }

    pub fn normalize_batch(
        &self,
        py: Python<'_>,
        texts: Vec<String>,
    ) -> Vec<String> {
        py.allow_threads(|| {
            texts.par_iter().map(|t| self.normalize_one(t)).collect()
        })
    }
}

impl TextNormalizer {
    fn normalize_one(&self, text: &str) -> String {
        let mut s: String = match self.unicode_form.as_str() {
            "NFC"  => text.nfc().collect(),
            "NFD"  => text.nfd().collect(),
            "NFKC" => text.nfkc().collect(),
            "NFKD" => text.nfkd().collect(),
            _      => text.nfc().collect(),
        };

        if self.strip_headers_footers {
            s = strip_headers_footers(&s);
        }

        if self.repair_ocr {
            s = repair_ocr_artifacts(&s);
        }

        if self.collapse_whitespace {
            s = collapse_whitespace(&s);
        }

        s
    }
}

/// Remove lines that repeat (similarity > 0.8) across form-feed page breaks.
/// No-op when no \f characters are present — documented behavior.
fn strip_headers_footers(text: &str) -> String {
    let pages: Vec<&str> = text.split('\x0c').collect();
    if pages.len() < 2 {
        return text.to_string();
    }

    // Collect lines that appear on more than half the pages.
    let all_lines: Vec<Vec<&str>> = pages.iter()
        .map(|p| p.lines().collect())
        .collect();

    // Collect every unique non-empty line from all pages, then keep only those
    // present on more than half the pages. Seeding from page 0 alone misses
    // running headers when page 0 is a cover page with no shared lines.
    let all_unique: std::collections::HashSet<&str> = all_lines.iter()
        .flat_map(|pg| pg.iter().copied())
        .filter(|l| !l.trim().is_empty())
        .collect();

    let candidate_lines: std::collections::HashSet<&str> = all_unique
        .into_iter()
        .filter(|line| {
            let trimmed = line.trim();
            let count = all_lines.iter()
                .filter(|page_lines| {
                    page_lines.iter().any(|l| l.trim() == trimmed)
                })
                .count();
            count * 2 > pages.len()
        })
        .collect();

    if candidate_lines.is_empty() {
        return text.to_string();
    }

    pages.iter()
        .map(|page| {
            page.lines()
                .filter(|l| !candidate_lines.contains(l.trim()))
                .collect::<Vec<_>>()
                .join("\n")
        })
        .collect::<Vec<_>>()
        .join("\x0c")
}

/// Heuristic OCR artifact repair for common Tesseract substitutions.
/// Uses capture groups — Rust's regex crate does not support lookaround.
fn repair_ocr_artifacts(text: &str) -> String {
    // ([a-z])rn([a-z]) → $1m$2  — 'rn' between lowercase letters
    let rn_to_m = regex::Regex::new(r"([a-z])rn([a-z])").unwrap();
    // (\d)l(\d) → ${1}1${2}  — 'l' between digits
    let l_between_digits = regex::Regex::new(r"(\d)l(\d)").unwrap();

    let s = rn_to_m.replace_all(text, "${1}m${2}");
    let s = l_between_digits.replace_all(&s, "${1}1${2}");
    s.into_owned()
}

fn collapse_whitespace(text: &str) -> String {
    // Replace runs of whitespace (excluding newlines) with a single space,
    // and collapse 3+ newlines to 2.
    let horizontal = regex::Regex::new(r"[^\S\n]+").unwrap();
    let excess_newlines = regex::Regex::new(r"\n{3,}").unwrap();

    let s = horizontal.replace_all(text, " ");
    let s = excess_newlines.replace_all(&s, "\n\n");
    s.trim().to_string()
}
