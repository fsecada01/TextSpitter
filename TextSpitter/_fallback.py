"""
Pure-Python fallback implementations for when the Rust extension is unavailable.

These match the interface of TextSpitter._core exactly, so callers can use
either path without branching.
"""

from __future__ import annotations

import unicodedata
from typing import Literal


def detect_encoding(data: bytes) -> str:
    """Detect encoding by trying common codecs in priority order."""
    if not data:
        return "utf-8"
    for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
        try:
            data.decode(enc)
            return enc
        except (UnicodeDecodeError, LookupError):
            continue
    return "utf-8"


class TextNormalizer:
    _NormForm = Literal["NFC", "NFD", "NFKC", "NFKD"]

    def __init__(
        self,
        unicode_form: _NormForm = "NFC",
        collapse_whitespace: bool = True,
        repair_ocr: bool = False,
        strip_headers_footers: bool = False,
    ) -> None:
        self.unicode_form: TextNormalizer._NormForm = unicode_form
        self.collapse_whitespace = collapse_whitespace
        self.repair_ocr = repair_ocr
        self.strip_headers_footers = strip_headers_footers

    def normalize(self, text: str) -> str:
        s = unicodedata.normalize(self.unicode_form, text)
        if self.strip_headers_footers:
            s = self._strip_headers(s)
        if self.repair_ocr:
            s = self._repair_ocr(s)
        if self.collapse_whitespace:
            import re

            s = re.sub(r"[^\S\n]+", " ", s)
            s = re.sub(r"\n{3,}", "\n\n", s)
            s = s.strip()
        return s

    def normalize_batch(self, texts: list[str]) -> list[str]:
        return [self.normalize(t) for t in texts]

    def _strip_headers(self, text: str) -> str:
        pages = text.split("\x0c")
        if len(pages) < 2:
            return text
        all_lines = [p.splitlines() for p in pages]
        candidates = {
            ln.strip()
            for ln in all_lines[0]
            if ln.strip()
            and sum(
                1
                for pl in all_lines
                if ln.strip() in [row.strip() for row in pl]
            )
            * 2
            > len(pages)
        }
        return "\x0c".join(
            "\n".join(
                row
                for row in page.splitlines()
                if row.strip() not in candidates
            )
            for page in pages
        )

    def _repair_ocr(self, text: str) -> str:
        import re

        text = re.sub(r"([a-z])rn([a-z])", r"\1m\2", text)
        text = re.sub(r"(\d)l(\d)", r"\g<1>1\2", text)
        return text


class Chunk:
    def __init__(
        self,
        text: str,
        token_count: int,
        char_start: int,
        char_end: int,
        section_title: str | None,
        chunk_index: int,
        total_chunks: int | None,
        metadata: dict,
    ) -> None:
        self.text = text
        self.token_count = token_count
        self.char_start = char_start
        self.char_end = char_end
        self.section_title = section_title
        self.chunk_index = chunk_index
        self.total_chunks = total_chunks
        self.metadata = metadata

    def __repr__(self) -> str:
        return (
            f"Chunk(index={self.chunk_index}/{self.total_chunks}, "
            f"tokens={self.token_count}, "
            f"chars={self.char_start}..{self.char_end})"
        )


class TextChunker:
    def __init__(
        self,
        max_tokens: int = 2000,
        min_tokens: int = 100,
        tokenizer: str = "cl100k_base",
        preserve_tables: bool = True,
        section_patterns: list[str] | None = None,
    ) -> None:
        if min_tokens > max_tokens:
            raise ValueError(
                f"min_tokens ({min_tokens}) must be "
                f"<= max_tokens ({max_tokens})"
            )
        try:
            import tiktoken

            tiktoken.get_encoding(tokenizer)
        except ImportError:
            pass
        self.max_tokens = max_tokens
        self.min_tokens = min_tokens
        self.tokenizer = tokenizer
        self.preserve_tables = preserve_tables
        self.section_patterns = section_patterns or []

    def _count(self, text: str) -> int:
        try:
            import tiktoken

            enc = tiktoken.get_encoding(self.tokenizer)
            return len(enc.encode(text))
        except Exception:
            # Rough character-based fallback: ~4 chars per token
            return len(text) // 4

    def chunk(self, text: str) -> list[Chunk]:
        import re

        paragraphs = [p.strip() for p in re.split(r"\n\n+", text) if p.strip()]
        chunks: list[Chunk] = []
        current_parts: list[str] = []
        current_tokens = 0
        char_cursor = 0
        current_start = 0
        section_title: str | None = None

        for para in paragraphs:
            para_tokens = self._count(para)
            if current_tokens + para_tokens > self.max_tokens and current_parts:
                chunk_text = "\n\n".join(current_parts)
                chunks.append(
                    Chunk(
                        text=chunk_text,
                        token_count=current_tokens,
                        char_start=current_start,
                        char_end=char_cursor,
                        section_title=section_title,
                        chunk_index=0,
                        total_chunks=None,
                        metadata={},
                    )
                )
                current_parts = []
                current_tokens = 0
                current_start = char_cursor

            current_parts.append(para)
            current_tokens += para_tokens
            char_cursor += len(para) + 2  # +2 for \n\n

        if current_parts:
            chunk_text = "\n\n".join(current_parts)
            chunks.append(
                Chunk(
                    text=chunk_text,
                    token_count=current_tokens,
                    char_start=current_start,
                    char_end=char_cursor,
                    section_title=section_title,
                    chunk_index=0,
                    total_chunks=None,
                    metadata={},
                )
            )

        total = len(chunks)
        for i, c in enumerate(chunks):
            c.chunk_index = i
            c.total_chunks = total
        return chunks

    def chunk_batch(self, texts: list[str]) -> list[list[Chunk]]:
        return [self.chunk(t) for t in texts]


class TokenCounter:
    def __init__(self, model: str = "cl100k_base") -> None:
        try:
            import tiktoken

            tiktoken.get_encoding(model)
        except ImportError:
            pass
        self.model = model

    def _bpe(self):
        try:
            import tiktoken

            return tiktoken.get_encoding(self.model)
        except Exception:
            return None

    def count(self, text: str) -> int:
        bpe = self._bpe()
        return len(bpe.encode(text)) if bpe else len(text) // 4

    def count_batch(self, texts: list[str]) -> list[int]:
        return [self.count(t) for t in texts]

    def truncate(
        self, text: str, max_tokens: int, strategy: str = "end"
    ) -> str:
        bpe = self._bpe()
        if bpe is None:
            # Word-based approximation: ~1 token per word
            words = text.split()
            if len(words) <= max_tokens:
                return text
            if strategy == "middle":
                half = max_tokens // 2
                kept = words[:half] + words[-(max_tokens - half) :]
            else:
                kept = words[:max_tokens]
            return " ".join(kept)
        tokens = bpe.encode(text)
        if len(tokens) <= max_tokens:
            return text
        if strategy == "middle":
            half = max_tokens // 2
            kept = tokens[:half] + tokens[-(max_tokens - half) :]
        else:
            kept = tokens[:max_tokens]
        return bpe.decode(kept)
