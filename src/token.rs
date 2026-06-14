use pyo3::prelude::*;
use rayon::prelude::*;
use tiktoken_rs::{get_bpe_from_model, CoreBPE};

/// Resolve an encoding name ("cl100k_base") or model name ("gpt-4") to a BPE.
fn load_bpe(name: &str) -> Result<CoreBPE, String> {
    let result = match name {
        "cl100k_base" => tiktoken_rs::cl100k_base(),
        "o200k_base"  => tiktoken_rs::o200k_base(),
        "r50k_base"   => tiktoken_rs::r50k_base(),
        "p50k_base"   => tiktoken_rs::p50k_base(),
        "p50k_edit"   => tiktoken_rs::p50k_edit(),
        // Fall through to model-name lookup (e.g. "gpt-4" → cl100k_base)
        other         => get_bpe_from_model(other),
    };
    result.map_err(|e| e.to_string())
}

#[pyclass]
pub struct TokenCounter {
    model: String,
}

#[pymethods]
impl TokenCounter {
    #[new]
    #[pyo3(signature = (model = "cl100k_base".to_string()))]
    pub fn new(model: String) -> PyResult<Self> {
        load_bpe(&model)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(
                format!("Unknown tiktoken model '{}': {}", model, e)
            ))?;
        Ok(Self { model })
    }

    pub fn count(&self, text: &str) -> PyResult<usize> {
        let bpe = load_bpe(&self.model)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e))?;
        Ok(bpe.encode_with_special_tokens(text).len())
    }

    pub fn count_batch(
        &self,
        py: Python<'_>,
        texts: Vec<String>,
    ) -> PyResult<Vec<usize>> {
        let model = self.model.clone();
        py.allow_threads(|| {
            texts.par_iter()
                .map(|t| {
                    load_bpe(&model)
                        .map(|bpe| bpe.encode_with_special_tokens(t).len())
                })
                .collect::<Result<Vec<_>, _>>()
        })
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(e))
    }

    /// Truncate text to at most ``max_tokens`` tokens.
    ///
    /// Strategies:
    /// - ``"end"``    — keep the start, drop from the end.
    /// - ``"middle"`` — keep start and end, drop the middle.
    /// - ``"smart"``  — position-weighted; drop lowest-scored first.
    #[pyo3(signature = (text, max_tokens, strategy = "end".to_string()))]
    pub fn truncate(
        &self,
        text: &str,
        max_tokens: usize,
        strategy: String,
    ) -> PyResult<String> {
        let bpe = load_bpe(&self.model)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e))?;

        let tokens = bpe.encode_with_special_tokens(text);
        if tokens.len() <= max_tokens {
            return Ok(text.to_string());
        }

        let kept = match strategy.as_str() {
            "middle" => {
                let half = max_tokens / 2;
                let mut t = tokens[..half].to_vec();
                t.extend_from_slice(&tokens[tokens.len() - (max_tokens - half)..]);
                t
            }
            "smart" => truncate_smart(&tokens, max_tokens),
            _ => tokens[..max_tokens].to_vec(),
        };

        bpe.decode(kept)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))
    }
}

fn truncate_smart(tokens: &[usize], max_tokens: usize) -> Vec<usize> {
    // Weight the head 2:1 over the tail — beginning of document carries more
    // context; middle is dropped first, then tail is trimmed before head.
    let n = tokens.len();
    let keep_start = (max_tokens * 2).div_ceil(3);
    let keep_end = max_tokens - keep_start;
    let tail_start = n.saturating_sub(keep_end);

    if keep_end == 0 || tail_start <= keep_start {
        tokens[..max_tokens.min(n)].to_vec()
    } else {
        let mut result = tokens[..keep_start].to_vec();
        result.extend_from_slice(&tokens[tail_start..]);
        result
    }
}
