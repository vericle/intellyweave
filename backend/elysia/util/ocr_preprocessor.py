"""
Multilingual OCR text post-processing utilities.

Features:
- Fixes encoding / mojibake via `ftfy`.
- Normalizes whitespace, punctuation, and line breaks.
- Cleans unwanted / weird characters using `clean-text`.
- Repairs common OCR artifacts such as hyphenated line breaks.
- Spell correction using:
    - SymSpellPy (if dictionary registered)
    - Fallback to pyspellchecker
- OCR noise detection (is_ocr_text) based on:
    - misspelling ratio
    - noise character ratio
    - hyphenated line-break artifacts

Assumptions:
- All dependencies are installed:
    ftfy, langdetect, pyspellchecker, symspellpy, clean-text
"""

from __future__ import annotations

import logging
import re
import unicodedata
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import ftfy
from cleantext import clean as clean_text
from langdetect import DetectorFactory, LangDetectException, detect
from spellchecker import SpellChecker
from symspellpy import SymSpell, Verbosity

logger = logging.getLogger(__name__)

# Make langdetect deterministic
DetectorFactory.seed = 0

# Registry of SymSpell instances by language code ("en", "de", "ru", etc.)
_SYMSPELL_REGISTRY: Dict[str, SymSpell] = {}


@dataclass(frozen=True)
class OCRPreprocessorConfig:
    """
    Configuration for OCR text preprocessing.

    Attributes:
        enable_spell_check:
            Whether to apply spell correction after structural cleanup.
        spell_engine:
            "auto"         → try SymSpell if available, then pyspellchecker.
            "symspell"     → only SymSpell (no fallback).
            "pyspellchecker" → only pyspellchecker.
            "none"         → no spelling correction.
        max_chars_for_spell_check:
            Upper bound on characters to feed through the spell engine.
        language_hint:
            Optional ISO language code (e.g. "de", "en", "ru").
            If provided, this is preferred over auto-detection.
        aggressive_hyphen_fix:
            If True, attempts to remove hyphenation at line ends.
        normalize_whitespace:
            If True, collapses repeated whitespace and normalizes newlines.
        symspell_max_edit_distance:
            Max edit distance for SymSpell lookup.
    """

    enable_spell_check: bool = True
    spell_engine: str = "auto"  # "auto" | "symspell" | "pyspellchecker" | "none"
    max_chars_for_spell_check: int = 10_000
    language_hint: Optional[str] = None
    aggressive_hyphen_fix: bool = True
    normalize_whitespace: bool = True
    symspell_max_edit_distance: int = 2


DEFAULT_CONFIG = OCRPreprocessorConfig()


# ---------------------------------------------------------------------------
# SymSpell registration API
# ---------------------------------------------------------------------------


def register_symspell_dictionary(
    lang: str,
    dictionary_path: str,
    bigram_path: Optional[str] = None,
    max_edit_distance: int = 2,
    prefix_length: int = 7,
    separator: str = "\t",
    term_index: int = 0,
    count_index: int = 1,
) -> None:
    """
    Register a SymSpell instance for a given language using frequency files.

    Call this ONCE at application startup per language you care about.

    Args:
        lang:
            Language code (e.g. "en", "de", "ru").
        dictionary_path:
            Path to a term-frequency dictionary file:
                <term><separator><count>
        bigram_path:
            Optional path to a bigram frequency file.
        max_edit_distance:
            Max edit distance for the SymSpell instance.
        prefix_length:
            Prefix length for SymSpell indexing.
        separator:
            Field separator used in the dictionary file.
        term_index:
            Column index for the term.
        count_index:
            Column index for the term frequency.
    """
    language_key = lang.lower().strip()
    symspell = SymSpell(
        max_dictionary_edit_distance=max_edit_distance,
        prefix_length=prefix_length,
    )

    loaded = symspell.load_dictionary(
        dictionary_path,
        term_index=term_index,
        count_index=count_index,
        separator=separator,
    )
    if not loaded:
        raise ValueError(f"Failed to load SymSpell dictionary from {dictionary_path!r}")

    if bigram_path:
        symspell.load_bigram_dictionary(
            bigram_path,
            term_index=term_index,
            count_index=count_index,
            separator=separator,
        )

    _SYMSPELL_REGISTRY[language_key] = symspell
    logger.info("Registered SymSpell dictionary for language %s", language_key)


def register_symspell_instance(lang: str, symspell: SymSpell) -> None:
    """
    Directly register a pre-configured SymSpell instance for a language.

    Useful for tests or when you programmatically build dictionaries.
    """
    language_key = lang.lower().strip()
    _SYMSPELL_REGISTRY[language_key] = symspell
    logger.info("Registered custom SymSpell instance for language %s", language_key)


def _get_symspell(lang: Optional[str]) -> Optional[SymSpell]:
    if not lang:
        return None
    return _SYMSPELL_REGISTRY.get(lang.lower().strip())


# ---------------------------------------------------------------------------
# Public API: Preprocessing
# ---------------------------------------------------------------------------


def preprocess_ocr_text(
    text: str,
    config: OCRPreprocessorConfig | None = None,
) -> str:
    """
    High-level OCR text cleanup pipeline.

    Safe for multilingual European text, including Latin & Cyrillic.

    Steps:
        1. ftfy encoding fix.
        2. Normalize line endings.
        3. Remove hyphenation line-break artifacts.
        4. Merge broken lines.
        5. clean-text cleanup (unicode noise, whitespace).
        6. Custom spacing & punctuation normalization.
        7. Spell correction via SymSpell / pyspellchecker (optional).

    Args:
        text:
            Raw OCR output text.
        config:
            Optional configuration. If omitted, DEFAULT_CONFIG is used.

    Returns:
        Cleaned text.
    """
    if text is None or text == "":
        return text

    # Preserve whitespace-only strings as-is
    if text.strip() == "":
        return text

    cfg = config or DEFAULT_CONFIG
    original_len = len(text)

    logger.info(
        "Starting OCR preprocessing (length=%s, aggressive_hyphen_fix=%s, normalize_whitespace=%s)",
        original_len,
        cfg.aggressive_hyphen_fix,
        cfg.normalize_whitespace,
    )

    # 1. Fix encoding / mojibake
    text = _fix_encoding(text)

    # 2. Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 3. Remove hyphenation at line ends
    if cfg.aggressive_hyphen_fix:
        logger.debug("Applying aggressive hyphen fix")
        text = _remove_hyphenated_line_breaks(text)

    # 4. Merge broken lines within paragraphs
    text = _merge_broken_lines(text)

    # 5. clean-text normalization (unicode noise, weird chars)
    text = _clean_with_cleantext(text)

    # 6. Fine-grained spacing & punctuation normalization
    if cfg.normalize_whitespace:
        text = _normalize_spacing_and_punctuation(text)

    # 7. Spell-checking (SymSpell → PySpell → none)
    detected_lang = _detect_language_safe(
        text,
        hint=cfg.language_hint,
    )
    logger.debug("Detected OCR language: %s", detected_lang)

    text = _apply_spell_correction(text, cfg, detected_lang)

    logger.debug(
        "OCR preprocessing completed: %d -> %d chars (lang=%s)",
        original_len,
        len(text),
        detected_lang,
    )
    return text


# ---------------------------------------------------------------------------
# Encoding & normalization helpers
# ---------------------------------------------------------------------------


def _fix_encoding(text: str) -> str:
    """Fix common encoding problems (mojibake) and normalize Unicode."""
    return ftfy.fix_text(text)


def _detect_language_safe(text: str, hint: Optional[str] = None) -> Optional[str]:
    """Detect language using langdetect, with optional hint override."""
    if hint:
        return hint.lower().strip()

    sample = text.strip()
    if len(sample) < 30:
        return None

    try:
        lang = detect(sample[:1000])
        return lang.lower().strip()
    except LangDetectException:
        logger.debug("Language detection failed; leaving language unset")
        return None
    except Exception as exc:
        logger.debug("Language detection error: %s", exc)
        return None


def _remove_hyphenated_line_breaks(text: str) -> str:
    """
    Remove hyphenation at line ends:

        "hyphen-\nated" -> "hyphenated"
    """
    return re.sub(r"-\s*\n\s*", "", text)


def _merge_broken_lines(text: str) -> str:
    """
    Merge lines where OCR introduced spurious line breaks inside paragraphs.

    - Keeps blank lines as paragraph separators.
    - Converts single line breaks inside paragraphs into spaces when appropriate.
    """

    def _merge_block(block: str) -> str:
        # Within a paragraph block, replace `word\nword` with `word word`
        return re.sub(r"(?<=\w)\n(?=\w)", " ", block)

    blocks = re.split(r"\n{2,}", text)
    merged_blocks = [_merge_block(b) for b in blocks]
    return "\n\n".join(merged_blocks)


def _clean_with_cleantext(text: str) -> str:
    """
    Use clean-text to normalize unicode noise and whitespace,
    without lowercasing or stripping punctuation/numbers.

    The clean-text library's clean() function has these parameters:
    - clean_all: if True, applies all cleaning (default True)
    - extra_spaces: remove extra spaces
    - stemming: apply stemming
    - stopwords: remove stopwords
    - lowercase: convert to lowercase
    - numbers: remove numbers
    - punct: remove punctuation

    We want minimal cleaning to preserve the original text structure,
    so we disable most features and only use extra_spaces.
    """
    return clean_text(
        text,
        clean_all=False,  # disable all default cleaning
        extra_spaces=True,  # only remove extra spaces
        stemming=False,  # don't apply stemming
        stopwords=False,  # keep stopwords
        lowercase=False,  # preserve case
        numbers=False,  # keep numbers
        punct=False,  # keep punctuation
    )


def _normalize_spacing_and_punctuation(text: str) -> str:
    """
    Normalize whitespace and common punctuation issues.

    - Collapse multiple spaces / tabs.
    - Normalize newlines to at most two in a row.
    - Remove spaces before punctuation.
    - Ensure a space after sentence-ending punctuation.
    """
    # Collapse horizontal whitespace
    text = re.sub(r"[ \t\f\v]+", " ", text)

    # Normalize consecutive newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Strip spaces at line boundaries
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n[ \t]+", "\n", text)

    # Remove spaces before punctuation like , . ; : ! ?
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)

    # Ensure a space after sentence ending punctuation when followed by a letter
    text = re.sub(r"([.!?])([^\s0-9])", r"\1 \2", text)

    return text.strip()


# ---------------------------------------------------------------------------
# Spell correction (SymSpell + pyspellchecker)
# ---------------------------------------------------------------------------


def _apply_spell_correction(
    text: str,
    cfg: OCRPreprocessorConfig,
    lang: Optional[str],
) -> str:
    """
    Apply spell correction using SymSpell and/or pyspellchecker depending on config.
    """
    if not text or not cfg.enable_spell_check:
        return text

    if len(text) > cfg.max_chars_for_spell_check:
        logger.debug(
            "Skipping spell check: text length %d > max_chars=%d",
            len(text),
            cfg.max_chars_for_spell_check,
        )
        return text

    engine = (cfg.spell_engine or "auto").lower().strip()
    logger.debug("Spell correction configured engine=%s", engine)

    # If language is unknown, we don't try to be smart
    if not lang:
        logger.debug("Skipping spell check: language unknown")
        return text

    # Try SymSpell if requested/allowed
    if engine in ("symspell", "auto"):
        sym = _get_symspell(lang)
        if sym is not None:
            try:
                corrected = _spell_correct_with_symspell(text, sym, cfg)
                logger.info("SymSpell correction applied (lang=%s)", lang)
                return corrected
            except Exception as exc:
                logger.debug("SymSpell correction failed: %s", exc)
                if engine == "symspell":
                    return text  # do not fall back
                # else fall through to pyspell

    # Try pyspellchecker if requested/allowed
    if engine in ("pyspellchecker", "auto"):
        try:
            corrected = _spell_correct_with_pyspellchecker(text, lang)
            logger.info("pyspellchecker correction applied (lang=%s)", lang)
            return corrected
        except Exception as exc:
            logger.debug("pyspellchecker correction failed: %s", exc)
            return text

    # Engine = "none" or unknown string
    return text


def _spell_correct_with_symspell(
    text: str,
    symspell: SymSpell,
    cfg: OCRPreprocessorConfig,
) -> str:
    """Spell correction using a SymSpell instance."""

    def _correct(core: str) -> str:
        if not _eligible_for_correction(core):
            return core
        suggestions = symspell.lookup(
            core,
            Verbosity.CLOSEST,
            max_edit_distance=cfg.symspell_max_edit_distance,
        )
        if not suggestions:
            return core
        return suggestions[0].term

    return _correct_tokens_generic(text, _correct)


def _spell_correct_with_pyspellchecker(text: str, lang: str) -> str:
    """Spell correction using pyspellchecker."""

    spell = SpellChecker(language=lang)

    def _correct(core: str) -> str:
        if not _eligible_for_correction(core):
            return core

        lower = core.lower()
        if lower in spell:
            return core

        suggestion = spell.correction(lower)
        if not suggestion:
            return core
        return suggestion

    return _correct_tokens_generic(text, _correct)


def _eligible_for_correction(core: str) -> bool:
    """
    Decide if a token core should be sent to a spell engine.

    We skip:
        - very short words (<=2)
        - all-uppercase words
        - anything containing digits
        - tokens without any letters
    """
    if len(core) <= 2:
        return False
    if core.isupper():
        return False
    if any(ch.isdigit() for ch in core):
        return False
    if not _has_letter(core):
        return False
    return True


def _correct_tokens_generic(
    text: str,
    correct_core: Callable[[str], str],
) -> str:
    """
    Generic token-level spelling correction.

    - Splits tokens into leading punctuation, core, trailing punctuation.
    - Sends core through `correct_core`.
    - Preserves original casing for first character when appropriate.
    """
    tokens = text.split()
    corrected_tokens: List[str] = []

    for token in tokens:
        leading, core, trailing = _split_token_punctuation(token)

        if not core:
            corrected_tokens.append(token)
            continue

        corrected_core = correct_core(core)

        # If we changed the core, preserve capitalization of the first letter
        if core[0].isupper() and corrected_core:
            corrected_core = corrected_core[0].upper() + corrected_core[1:]

        corrected_tokens.append(f"{leading}{corrected_core}{trailing}")

    return " ".join(corrected_tokens)


def _split_token_punctuation(token: str) -> Tuple[str, str, str]:
    """
    Split a token into (leading_punct, core, trailing_punct),
    respecting Unicode punctuation.
    """
    if not token:
        return "", "", ""

    start = 0
    end = len(token)

    while start < end and _is_punctuation(token[start]):
        start += 1
    while end > start and _is_punctuation(token[end - 1]):
        end -= 1

    leading = token[:start]
    core = token[start:end]
    trailing = token[end:]
    return leading, core, trailing


def _has_letter(token: str) -> bool:
    """True if the token contains at least one letter (Unicode-aware)."""
    return any(ch.isalpha() for ch in token)


def _is_punctuation(ch: str) -> bool:
    """Unicode-aware punctuation check."""
    return bool(ch) and unicodedata.category(ch).startswith("P")


# ---------------------------------------------------------------------------
# OCR noise detection (is_ocr_text)
# ---------------------------------------------------------------------------


def is_ocr_text(
    text: str, language_hint: Optional[str] = None, filename: Optional[str] = None
) -> bool:
    """
    Heuristic detector: "Does this text look like raw OCR output?"

    Combines:
        - Dictionary-based misspelling ratio (pyspellchecker).
        - Ratio of "noise" characters (non-letter, non-digit, non-punct).
        - Count of hyphenated line breaks.

    The threshold is tuned to be conservative:
    - Clean normal text → False
    - Text with typical OCR artifacts → True

    Special case: All .txt files are considered OCR text to ensure preprocessing.
    """
    # Bypass: All .txt files are considered OCR text
    if filename and filename.lower().endswith(".txt"):
        logger.debug("OCR detection bypassed: .txt file extension detected")
        return True

    if not text or len(text) < 40:
        return False

    lang = _detect_language_safe(text, hint=language_hint)

    tokens = _extract_word_tokens(text)
    if not tokens:
        return False

    miss_ratio = _estimate_misspelling_ratio(tokens, lang)
    noise_ratio = _estimate_noise_char_ratio(text)
    hyphen_breaks = len(re.findall(r"-\s*\n", text))

    score = 0.0
    if miss_ratio >= 0.0:
        score += miss_ratio
    score += noise_ratio * 0.6
    if hyphen_breaks:
        score += min(hyphen_breaks / 20.0, 0.5)

    logger.debug(
        "OCR detection: lang=%s miss_ratio=%.3f noise_ratio=%.3f "
        "hyphen_breaks=%d score=%.3f",
        lang,
        miss_ratio,
        noise_ratio,
        hyphen_breaks,
        score,
    )

    return score >= 0.4


def _extract_word_tokens(text: str) -> List[str]:
    """Extract word tokens using Unicode-aware \\w."""
    return re.findall(r"\w+", text, flags=re.UNICODE)


def _estimate_misspelling_ratio(
    tokens: Sequence[str],
    lang: Optional[str],
) -> float:
    """
    Estimate misspelling ratio using pyspellchecker.

    Returns:
        Ratio in [0.0, 1.0] or -1.0 if no usable dictionary.
    """
    if not lang:
        return -1.0

    content_tokens = [
        t.lower() for t in tokens if len(t) > 2 and all(ch.isalpha() for ch in t)
    ]
    if not content_tokens:
        return -1.0

    sample = content_tokens[:1000]

    try:
        spell = SpellChecker(language=lang)
    except Exception as exc:
        logger.debug("SpellChecker init failed for OCR detection: %s", exc)
        return -1.0

    try:
        misspelled = spell.unknown(sample)
    except Exception as exc:
        logger.debug("SpellChecker.unknown() failed: %s", exc)
        return -1.0

    return len(misspelled) / float(len(sample)) if sample else -1.0


def _estimate_noise_char_ratio(text: str) -> float:
    """
    Measure fraction of "weird" characters.

    Normal:
        - letters
        - digits
        - whitespace
        - punctuation

    Everything else counts as noise.
    """
    if not text:
        return 0.0

    normal = 0
    total = 0

    for ch in text:
        total += 1
        if ch.isspace():
            normal += 1
            continue

        cat = unicodedata.category(ch)
        if (
            cat.startswith("L")  # Letter
            or cat.startswith("N")  # Number
            or cat.startswith("P")  # Punctuation
        ):
            normal += 1

    if total == 0:
        return 0.0

    noise = total - normal
    return noise / float(total)


# ---------------------------------------------------------------------------
# Debug helper
# ---------------------------------------------------------------------------


def summarize_ocr_noise(text: str, language_hint: Optional[str] = None) -> dict:
    """
    Return internal OCR noise metrics used by is_ocr_text.

    Useful for debugging, logging, or monitoring OCR quality.
    """
    lang = _detect_language_safe(text, hint=language_hint)
    tokens = _extract_word_tokens(text)
    miss_ratio = _estimate_misspelling_ratio(tokens, lang)
    noise_ratio = _estimate_noise_char_ratio(text)
    hyphen_breaks = len(re.findall(r"-\s*\n", text))

    score = 0.0
    if miss_ratio >= 0.0:
        score += miss_ratio
    score += noise_ratio * 0.6
    score += min(hyphen_breaks / 20.0, 0.5)

    return {
        "language": lang,
        "misspelling_ratio": miss_ratio,
        "noise_char_ratio": noise_ratio,
        "hyphen_breaks": hyphen_breaks,
        "score": score,
        "is_ocr": score >= 0.4,
    }


__all__ = [
    "OCRPreprocessorConfig",
    "preprocess_ocr_text",
    "is_ocr_text",
    "summarize_ocr_noise",
    "register_symspell_dictionary",
    "register_symspell_instance",
]
