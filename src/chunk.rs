use pyo3::prelude::*;
use rayon::prelude::*;
use std::collections::HashMap;
use tiktoken_rs::{get_bpe_from_model, CoreBPE};

fn load_bpe(name: &str) -> Result<CoreBPE, String> {
    let result = match name {
        "cl100k_base" => tiktoken_rs::cl100k_base(),
        "o200k_base"  => tiktoken_rs::o200k_base(),
        "r50k_base"   => tiktoken_rs::r50k_base(),
        "p50k_base"   => tiktoken_rs::p50k_base(),
        "p50k_edit"   => tiktoken_rs::p50k_edit(),
        other         => get_bpe_from_model(other),
    };
    result.map_err(|e| e.to_string())
}

/// A single chunk produced by ``TextChunker``.
#[pyclass(get_all)]
#[derive(Clone, Debug)]
pub struct Chunk {
    /// The chunk text.
    pub text: String,
    /// BPE token count for this chunk.
    pub token_count: usize,
    /// Unicode code-point start offset in the original input string.
    pub char_start: usize,
    /// Unicode code-point end offset (exclusive) in the original input string.
    pub char_end: usize,
    /// Enclosing section header, if detected.
    pub section_title: Option<String>,
    /// Zero-based position in the chunk sequence.
    pub chunk_index: usize,
    /// Total chunks in the sequence (None when produced by chunk_iter).
    pub total_chunks: Option<usize>,
    /// Extra metadata (e.g. {"oversized": true}).
    pub metadata: HashMap<String, bool>,
}

#[pymethods]
impl Chunk {
    fn __repr__(&self) -> String {
        format!(
            "Chunk(index={}/{:?}, tokens={}, chars={}..{})",
            self.chunk_index,
            self.total_chunks,
            self.token_count,
            self.char_start,
            self.char_end,
        )
    }
}

#[pyclass]
pub struct TextChunker {
    max_tokens: usize,
    min_tokens: usize,
    tokenizer: String,
    preserve_tables: bool,
    section_patterns: Vec<String>,
}

#[pymethods]
impl TextChunker {
    #[new]
    #[pyo3(signature = (
        max_tokens = 2000,
        min_tokens = 100,
        tokenizer = "cl100k_base".to_string(),
        preserve_tables = true,
        section_patterns = vec![],
    ))]
    pub fn new(
        max_tokens: usize,
        min_tokens: usize,
        tokenizer: String,
        preserve_tables: bool,
        section_patterns: Vec<String>,
    ) -> PyResult<Self> {
        if min_tokens > max_tokens {
            return Err(pyo3::exceptions::PyValueError::new_err(format!(
                "min_tokens ({min_tokens}) must be <= max_tokens ({max_tokens})"
            )));
        }
        // Validate tokenizer name at construction time.
        load_bpe(&tokenizer)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e))?;
        Ok(Self { max_tokens, min_tokens, tokenizer, preserve_tables, section_patterns })
    }

    /// Chunk text into a list of ``Chunk`` objects.
    pub fn chunk(&self, text: &str) -> PyResult<Vec<Chunk>> {
        let chunks = self.split(text)?;
        let total = chunks.len();
        Ok(chunks.into_iter().enumerate().map(|(i, mut c)| {
            c.chunk_index = i;
            c.total_chunks = Some(total);
            c
        }).collect())
    }

    /// Chunk a batch of texts in parallel (GIL released).
    pub fn chunk_batch(
        &self,
        py: Python<'_>,
        texts: Vec<String>,
    ) -> PyResult<Vec<Vec<Chunk>>> {
        // Capture config for use inside the thread closure.
        let max_tokens = self.max_tokens;
        let min_tokens = self.min_tokens;
        let tokenizer = self.tokenizer.clone();
        let preserve_tables = self.preserve_tables;
        let section_patterns = self.section_patterns.clone();

        py.allow_threads(|| {
            texts.par_iter()
                .map(|text| {
                    let chunker = TextChunker {
                        max_tokens,
                        min_tokens,
                        tokenizer: tokenizer.clone(),
                        preserve_tables,
                        section_patterns: section_patterns.clone(),
                    };
                    let chunks = chunker.split(text)?;
                    let total = chunks.len();
                    Ok(chunks.into_iter().enumerate().map(|(i, mut c)| {
                        c.chunk_index = i;
                        c.total_chunks = Some(total);
                        c
                    }).collect::<Vec<_>>())
                })
                .collect::<PyResult<Vec<_>>>()
        })
    }
}

impl TextChunker {
    fn split(&self, text: &str) -> PyResult<Vec<Chunk>> {
        let bpe = load_bpe(&self.tokenizer)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e))?;

        let section_re = self.build_section_regex();
        let table_re = if self.preserve_tables {
            Some(regex::Regex::new(r"(?m)^\|.+\|[ \t]*$").unwrap())
        } else {
            None
        };

        // Split text into logical units: tables (atomic) and paragraph blocks.
        let units = segment_units(text, table_re.as_ref(), section_re.as_ref());

        let mut chunks: Vec<Chunk> = Vec::new();
        let mut current_text = String::new();
        let mut current_start: usize = 0; // char offset
        let mut current_section: Option<String> = None;
        let mut char_cursor: usize = 0;

        for unit in units {
            let unit_tokens = bpe.encode_with_special_tokens(&unit.text).len();

            // If this unit alone exceeds max_tokens, emit it as an oversized chunk.
            if unit_tokens > self.max_tokens {
                // Flush any pending content first.
                if !current_text.is_empty() {
                    chunks.push(self.make_chunk(
                        &current_text,
                        &bpe,
                        current_start,
                        char_cursor,
                        current_section.clone(),
                        false,
                    ));
                    current_text.clear();
                    current_start = char_cursor;
                }
                let unit_len: usize = unit.text.chars().count();
                chunks.push(self.make_chunk(
                    &unit.text,
                    &bpe,
                    char_cursor,
                    char_cursor + unit_len,
                    unit.section_title.or(current_section.clone()),
                    true, // oversized
                ));
                char_cursor += unit_len;
                continue;
            }

            let pending_tokens = bpe.encode_with_special_tokens(&current_text).len();

            if pending_tokens + unit_tokens > self.max_tokens && !current_text.is_empty() {
                // Emit pending chunk if it meets min_tokens.
                let pending_count = bpe.encode_with_special_tokens(&current_text).len();
                if pending_count >= self.min_tokens || chunks.is_empty() {
                    chunks.push(self.make_chunk(
                        &current_text,
                        &bpe,
                        current_start,
                        char_cursor,
                        current_section.clone(),
                        false,
                    ));
                    current_text.clear();
                    current_start = char_cursor;
                }
            }

            if let Some(title) = &unit.section_title {
                current_section = Some(title.clone());
            }

            let unit_char_len = unit.text.chars().count();
            current_text.push_str(&unit.text);
            char_cursor += unit_char_len;
        }

        // Flush any remaining content.
        if !current_text.is_empty() {
            chunks.push(self.make_chunk(
                &current_text,
                &bpe,
                current_start,
                char_cursor,
                current_section,
                false,
            ));
        }

        Ok(chunks)
    }

    fn make_chunk(
        &self,
        text: &str,
        bpe: &tiktoken_rs::CoreBPE,
        char_start: usize,
        char_end: usize,
        section_title: Option<String>,
        oversized: bool,
    ) -> Chunk {
        let token_count = bpe.encode_with_special_tokens(text).len();
        let mut metadata = HashMap::new();
        if oversized {
            metadata.insert("oversized".to_string(), true);
        }
        Chunk {
            text: text.to_string(),
            token_count,
            char_start,
            char_end,
            section_title,
            chunk_index: 0,      // set by caller
            total_chunks: None,  // set by caller
            metadata,
        }
    }

    fn build_section_regex(&self) -> Option<regex::Regex> {
        let mut patterns = vec![
            r"^[A-Z][A-Z\s]{4,}$".to_string(),
            r"^\d+\.\s+[A-Z]".to_string(),
            r"^SECTION\s+\d+".to_string(),
            r"^Article\s+[IVX\d]+".to_string(),
        ];
        patterns.extend(self.section_patterns.iter().cloned());
        let combined = patterns.join("|");
        regex::Regex::new(&format!("(?m){combined}")).ok()
    }
}

struct Unit {
    text: String,
    section_title: Option<String>,
}

/// Segment text into atomic units: tables stay whole, text splits on
/// paragraph breaks and section headers.
fn segment_units(
    text: &str,
    table_re: Option<&regex::Regex>,
    section_re: Option<&regex::Regex>,
) -> Vec<Unit> {
    let mut units = Vec::new();
    let mut remaining = text;

    while !remaining.is_empty() {
        // Check for a table starting at the current position.
        if let Some(table_match) = table_re.and_then(|re| re.find(remaining)) {
            // Emit any text before the table.
            if table_match.start() > 0 {
                let before = &remaining[..table_match.start()];
                push_text_units(before, section_re, &mut units);
            }
            // Find the end of the table block (last consecutive table line).
            let table_end = find_table_end(remaining, table_match.start());
            units.push(Unit {
                text: remaining[table_match.start()..table_end].to_string(),
                section_title: None,
            });
            remaining = &remaining[table_end..];
        } else {
            push_text_units(remaining, section_re, &mut units);
            break;
        }
    }

    units
}

fn push_text_units(
    text: &str,
    section_re: Option<&regex::Regex>,
    units: &mut Vec<Unit>,
) {
    let mut current_section: Option<String> = None;

    for para in text.split("\n\n") {
        let trimmed = para.trim();
        if trimmed.is_empty() {
            continue;
        }

        let title = section_re
            .and_then(|re| re.find(trimmed))
            .map(|m| m.as_str().trim().to_string());

        if let Some(ref t) = title {
            current_section = Some(t.clone());
        }

        units.push(Unit {
            text: format!("{trimmed}\n\n"),
            section_title: title.or(current_section.clone()),
        });
    }
}

fn find_table_end(text: &str, start: usize) -> usize {
    let from = &text[start..];
    let mut end = start;
    for line in from.lines() {
        if line.trim_start().starts_with('|') {
            end += line.len() + 1; // +1 for newline
        } else if line.trim().is_empty() {
            end += line.len() + 1;
        } else {
            break;
        }
    }
    end.min(text.len())
}
