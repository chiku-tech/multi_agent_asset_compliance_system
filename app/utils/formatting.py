"""Shared formatting utilities for constructing LLM prompts from retrieved data."""

from typing import Any


def format_chunks_for_prompt(chunks: list[Any], *, separator: str = "\n\n") -> str:
    """Format retrieved document chunks as a structured text block for LLM prompts."""
    if not chunks:
        return "No documents retrieved."
    return separator.join(
        f"[{c['filename']} | page {c.get('page', 'N/A')} | {c['doc_type']}]\n{c['text']}"
        for c in chunks
    )
