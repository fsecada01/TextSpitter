use pyo3::prelude::*;

mod encoding;
mod normalize;
mod token;
mod chunk;
mod separator;

#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(encoding::detect_encoding, m)?)?;
    m.add_class::<normalize::TextNormalizer>()?;
    m.add_class::<token::TokenCounter>()?;
    m.add_class::<chunk::TextChunker>()?;
    m.add_class::<chunk::Chunk>()?;
    Ok(())
}
