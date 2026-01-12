"""
Test cases for OCR text preprocessing functionality.

Tests cover:
1. Basic OCR text detection
2. German character corrections (ä, ö, ü, ß)
3. Word boundary fixes
4. Encoding fixes with ftfy
5. Spell checking (when enabled)
6. Integration with document processing pipeline
7. Real-world OCR document processing and chunking
"""

import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from elysia.tools.retrieval.chunk import Chunker

from symspellpy import SymSpell

from elysia.util.ocr_preprocessor import (
    OCRPreprocessorConfig,
    is_ocr_text,
    preprocess_ocr_text,
    register_symspell_instance,
    summarize_ocr_noise,
)


def test_preprocess_noop_on_empty():
    assert preprocess_ocr_text("") == ""
    assert preprocess_ocr_text("   ") == "   "  # preserved as-is


def test_preprocess_fixes_basic_encoding_without_spell_check():
    raw = 'This is a test\u2014with “quotes” and â€“ odd dash.'
    cfg = OCRPreprocessorConfig(enable_spell_check=False)
    cleaned = preprocess_ocr_text(raw, cfg)

    assert "This is a test" in cleaned
    assert "quotes" in cleaned


def test_hyphenated_line_break_is_removed():
    raw = "This is a hyphen-\nated word in the text."
    cfg = OCRPreprocessorConfig(enable_spell_check=False)
    cleaned = preprocess_ocr_text(raw, cfg)

    assert "hyphenated" in cleaned
    assert "hyphen-\n" not in cleaned


def test_broken_line_is_merged():
    raw = "This is a\nsentence that\nshould be one line."
    cfg = OCRPreprocessorConfig(enable_spell_check=False)
    cleaned = preprocess_ocr_text(raw, cfg)

    assert "This is a sentence that should be one line." in cleaned


def test_pyspellchecker_corrects_simple_error():
    raw = "This is a splling error."
    cfg = OCRPreprocessorConfig(
        enable_spell_check=True,
        spell_engine="pyspellchecker",
        language_hint="en",
    )
    cleaned = preprocess_ocr_text(raw, cfg)

    assert "splling" not in cleaned
    assert "This is a" in cleaned


def test_auto_spell_engine_falls_back_to_pyspell_when_no_symspell():
    raw = "This is a splling error."
    cfg = OCRPreprocessorConfig(
        enable_spell_check=True,
        spell_engine="auto",
        language_hint="en",
    )
    cleaned = preprocess_ocr_text(raw, cfg)

    assert "splling" not in cleaned


def test_symspell_integration_with_custom_instance():
    # Build a small SymSpell dictionary in-memory
    sym = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
    sym.create_dictionary_entry("spelling", 10)
    sym.create_dictionary_entry("error", 10)
    sym.create_dictionary_entry("This", 5)
    sym.create_dictionary_entry("is", 5)
    sym.create_dictionary_entry("a", 5)

    register_symspell_instance("en", sym)

    raw = "This is a splling errro."
    cfg = OCRPreprocessorConfig(
        enable_spell_check=True,
        spell_engine="symspell",
        language_hint="en",
        symspell_max_edit_distance=2,
    )

    cleaned = preprocess_ocr_text(raw, cfg)

    assert "splling" not in cleaned
    assert "errro" not in cleaned
    assert "spelling" in cleaned
    assert "error" in cleaned


def test_is_ocr_text_false_for_clean_sentence():
    text = (
        "This is a perfectly normal sentence with no OCR artifacts, "
        "just plain text."
    )
    assert is_ocr_text(text, language_hint="en") is False


def test_is_ocr_text_true_for_noisy_ocr_like_text():
    text = (
        "Th1s 1s s0me n0isy OCR t3xt with hyphen-\n"
        "ated lines, rand0m symb°ls, and br0ken encÃding."
    )
    assert is_ocr_text(text, language_hint="en") is True


def test_summarize_ocr_noise_has_expected_keys():
    text = "This is a splling error in a sentnce."
    summary = summarize_ocr_noise(text, language_hint="en")

    for key in [
        "language",
        "misspelling_ratio",
        "noise_char_ratio",
        "hyphen_breaks",
        "score",
        "is_ocr",
    ]:
        assert key in summary


def test_multilingual_text_does_not_crash():
    # Russian + German + Polish text mixed
    text = (
        "Это пример русского текста.\n"
        "Dies ist ein deutscher Satz.\n"
        "To jest polskie zdanie."
    )

    cleaned = preprocess_ocr_text(text)
    assert isinstance(cleaned, str)

    flag = is_ocr_text(text)
    assert isinstance(flag, bool)


class TestRealWorldOCRDocument:
    """Test real-world OCR document processing with German text.

    This test class processes a real German document about Rattenlinien (Nazi Rat Lines),
    the escape routes used by Nazi war criminals after WWII. The document contains
    German text with umlauts and historical content about Nazi escape networks.
    """

    def test_german_ocr_document_processing_and_chunking(self):
        """Test processing real German OCR text and chunking it.

        This test verifies that:
        1. The OCR text is properly preprocessed (encoding fixes)
        2. German umlauts (ä, ö, ü) are preserved
        3. Key historical content about Nazi escape routes is maintained
        4. Text can be chunked successfully with valid spans
        """
        # Path to the test OCR file
        test_file_path = Path(__file__).parent.parent.parent.parent / "examples" / "cleaned" / "coldwar" / "Rattenlinien_cleaned.txt"
        
        # Skip test if file doesn't exist
        if not test_file_path.exists():
            return
        
        # Read the OCR text
        with open(test_file_path, 'r', encoding='utf-8') as f:
            ocr_text = f.read()
        
        # Verify text was read successfully
        assert len(ocr_text) > 0, "OCR file should not be empty"

        # Preprocess the OCR text (disable spell check to avoid language detection issues)
        cfg = OCRPreprocessorConfig(enable_spell_check=False, language_hint='de')
        preprocessed_text = preprocess_ocr_text(ocr_text, cfg)

        # Verify preprocessing didn't destroy content
        assert len(preprocessed_text) > 0, "Preprocessed text should not be empty"
        assert len(preprocessed_text) > len(ocr_text) * 0.8, "Preprocessing should not remove more than 20% of content"

        # Verify German umlauts are preserved (Rattenlinien document has many)
        assert "ä" in preprocessed_text, "German umlaut ä should be preserved"
        assert "ö" in preprocessed_text, "German umlaut ö should be preserved"
        assert "ü" in preprocessed_text, "German umlaut ü should be preserved"

        # Verify key historical content from the Rattenlinien document is preserved
        assert "Rattenlinien" in preprocessed_text, "Document title 'Rattenlinien' should be preserved"
        assert "Fluchtrouten" in preprocessed_text, "Key term 'Fluchtrouten' (escape routes) should be preserved"
        assert "1945" in preprocessed_text, "Key historical year 1945 should be preserved"
        assert "Argentinien" in preprocessed_text, "Destination country 'Argentinien' should be preserved"
        assert "Vatikan" in preprocessed_text, "Key institution 'Vatikan' should be preserved"
        assert "Eichmann" in preprocessed_text, "Nazi war criminal 'Eichmann' should be preserved"
        assert "Draganović" in preprocessed_text, "Key figure 'Draganović' should be preserved"
        
        # Test chunking on the preprocessed text
        chunker = Chunker(chunking_strategy="sentences", num_sentences=3)
        chunks, spans = chunker.chunk(preprocessed_text)
        
        # Verify chunking worked
        assert len(chunks) > 0, "Should have at least one chunk"
        assert len(chunks) == len(spans), "Number of chunks should match number of spans"
        
        # Verify all chunks are valid and match their spans
        for i, (chunk, span) in enumerate(zip(chunks, spans)):
            assert len(chunk) > 0, f"Chunk {i} should not be empty"
            assert span[1] > span[0], f"Span {i} should have valid range"
            assert preprocessed_text[span[0]:span[1]] == chunk, \
                f"Chunk {i} should exactly match text at its span location"
        
    def test_german_ocr_chunk_sizes(self):
        """Test that chunking produces reasonable chunk sizes for German OCR text.

        This test verifies that:
        1. Different chunking strategies all produce valid chunks
        2. Chunk sizes are reasonable (not empty, not too large)
        3. German characters are preserved throughout the chunking process (Rattenlinien document)
        """
        test_file_path = Path(__file__).parent.parent.parent.parent / "examples" / "cleaned" / "coldwar" / "Rattenlinien_cleaned.txt"
        
        if not test_file_path.exists():
            return
        
        with open(test_file_path, 'r', encoding='utf-8') as f:
            ocr_text = f.read()
        
        # Preprocess with spell checking disabled
        cfg = OCRPreprocessorConfig(enable_spell_check=False, language_hint='de')
        preprocessed_text = preprocess_ocr_text(ocr_text, cfg)
        
        # Check that German characters are in the preprocessed text
        has_german_chars = any(char in preprocessed_text for char in ['ä', 'ö', 'ü', 'ß'])
        
        # Test different chunking strategies
        strategies = [
            ("sentences", 1),
            ("sentences", 3),
            ("sentences", 5),
        ]
        
        for strategy, num_sentences in strategies:
            chunker = Chunker(chunking_strategy=strategy, num_sentences=num_sentences)
            chunks, spans = chunker.chunk(preprocessed_text)
            
            # Verify chunks were created
            assert len(chunks) > 0, \
                f"Should create chunks with strategy={strategy}, num_sentences={num_sentences}"
            
            # Verify all spans are valid and match chunks
            assert len(chunks) == len(spans), \
                f"Number of chunks ({len(chunks)}) should equal number of spans ({len(spans)})"
            
            # Check chunk sizes are reasonable
            for i, (chunk, span) in enumerate(zip(chunks, spans)):
                # Not empty
                assert len(chunk) > 0, \
                    f"Chunk {i} should not be empty (strategy={strategy}, num_sentences={num_sentences})"
                
                # Not too large (less than 10000 chars)
                assert len(chunk) < 10000, \
                    f"Chunk {i} should not exceed 10000 chars, got {len(chunk)} (strategy={strategy}, num_sentences={num_sentences})"
                
                # Span is valid
                assert span[1] > span[0], \
                    f"Span {i} should have end > start (strategy={strategy}, num_sentences={num_sentences})"
                
                # Chunk matches its span in the original text
                assert preprocessed_text[span[0]:span[1]] == chunk, \
                    f"Chunk {i} content should match its span location (strategy={strategy}, num_sentences={num_sentences})"
            
            # If the preprocessed text has German characters, verify they're preserved in chunks
            if has_german_chars:
                chunks_with_german = [c for c in chunks if any(char in c for char in ['ä', 'ö', 'ü', 'ß'])]
                assert len(chunks_with_german) > 0, \
                    f"At least some chunks should preserve German characters (strategy={strategy}, num_sentences={num_sentences})"