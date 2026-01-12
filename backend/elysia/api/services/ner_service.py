# ABOUTME: Service for named entity recognition using GLiNER model
import warnings
from threading import Lock
from typing import Any, Dict, List, Optional

from elysia.api.core.log import logger

# Suppress GLiNER-related warnings
warnings.filterwarnings("ignore", message=".*sentencepiece.*", category=UserWarning)
warnings.filterwarnings(
    "ignore",
    message=".*builtin type.*has no __module__ attribute.*",
    category=DeprecationWarning,
)
warnings.filterwarnings("ignore", category=DeprecationWarning, module=".*swig.*")
warnings.filterwarnings(
    "ignore", message=".*SwigPyPacked.*", category=DeprecationWarning
)

try:
    from gliner import GLiNER
except ImportError:
    GLiNER = None


GLINER_MODEL_NAME = "urchade/gliner_multi-v2.1"
# Pin to known cached revision to avoid re-downloading when remote repo updates
GLINER_MODEL_REVISION = "853ce23e47e519248ba3ec5953f002a80bffdedd"
_SHARED_NER_MODEL: Optional[Any] = None
_MODEL_INIT_LOCK = Lock()


def _load_shared_gliner_model() -> Optional[Any]:
    """Load GLiNER once per process to prevent repeated high-memory allocations."""

    global _SHARED_NER_MODEL

    if GLiNER is None:
        return None

    if _SHARED_NER_MODEL is not None:
        return _SHARED_NER_MODEL

    with _MODEL_INIT_LOCK:
        if _SHARED_NER_MODEL is not None:
            return _SHARED_NER_MODEL

        try:
            logger.info(
                "Loading GLiNER model '%s' for entity extraction...", GLINER_MODEL_NAME
            )
            with warnings.catch_warnings(record=False):
                warnings.simplefilter("ignore")
                # Try loading from cache first (fast), fall back to download for fresh installs
                try:
                    _SHARED_NER_MODEL = GLiNER.from_pretrained(
                        GLINER_MODEL_NAME,
                        revision=GLINER_MODEL_REVISION,
                        local_files_only=True,
                    )
                except (OSError, EnvironmentError, ValueError, Exception) as cache_err:
                    # Model not cached yet - download it (first run only)
                    # Catch broad exceptions as HuggingFace can raise various types:
                    # OSError, EnvironmentError, ValueError, LocalEntryNotFoundError, etc.
                    logger.info(
                        "Model not in cache (%s), downloading (this only happens once)...",
                        type(cache_err).__name__
                    )
                    _SHARED_NER_MODEL = GLiNER.from_pretrained(
                        GLINER_MODEL_NAME,
                        revision=GLINER_MODEL_REVISION,
                    )
            logger.info("GLiNER model initialized successfully")
        except Exception as e:  # pragma: no cover - defensive logging path
            logger.warning(f"Failed to load GLiNER model: {e}")
            _SHARED_NER_MODEL = None

    return _SHARED_NER_MODEL


class NamedEntityRecognitionService:
    """Service for extracting named entities from text using GLiNER"""

    def __init__(self):
        """
        Initialize the NER service with lazy-loaded GLiNER model
        """
        self._ner_model = None

    @property
    def ner_model(self):
        """
        Lazy load the GLiNER model only when first accessed.
        This avoids loading the model and its dependencies at service initialization.
        """
        if self._ner_model is None:
            self._ner_model = _load_shared_gliner_model()
        return self._ner_model

    def extract_entities(
        self, text: Optional[str], labels: Optional[List[str]] = None
    ) -> Dict[str, List[str]]:
        """
        Extract named entities from text using GLiNER

        Args:
            text: Text to extract entities from
            labels: Entity types to extract (e.g., ["location", "person", "organization"])

        Returns:
            Dictionary mapping entity types to lists of extracted entities
        """
        if not text:
            logger.debug("NER received empty text; skipping extraction")
            return {}

        # Access the lazy-loaded model
        model = self.ner_model
        if model is None:
            logger.warning("GLiNER model not available - skipping entity extraction")
            return {}

        if labels is None:
            labels = ["location", "person", "organization", "date", "law", "event"]

        logger.debug(
            "Running NER on %s chars with labels=%s",
            len(text),
            labels,
        )

        try:
            # GLiNER has a default max length of 384 tokens. To avoid truncation,
            # split long text into segments and process each segment separately
            max_tokens_per_segment = 350  # Leave some buffer below GLiNER's limit

            # Use spaCy for tokenization to split text appropriately
            # Note: This requires access to the chunker, so we'll use a simpler approach
            if len(text) <= max_tokens_per_segment * 4:  # Rough character estimate
                # Text is short enough, process normally
                entities = model.predict_entities(text, labels, threshold=0.5)
            else:
                # For long texts, split by sentences/paragraphs as fallback
                segments = self._split_text_into_segments(
                    text, max_tokens_per_segment * 4
                )
                logger.info(
                    "NER splitting long text into %s segments for processing",
                    len(segments),
                )
                entities = []
                for idx, segment in enumerate(segments, start=1):
                    segment_entities = model.predict_entities(
                        segment, labels, threshold=0.5
                    )
                    logger.debug(
                        "Segment %s produced %s raw entities",
                        idx,
                        len(segment_entities),
                    )
                    entities.extend(segment_entities)

            # Group entities by type
            entities_by_type = {}
            for entity in entities:
                entity_type = entity["label"]
                entity_text = entity["text"]

                if entity_type not in entities_by_type:
                    entities_by_type[entity_type] = []

                # Avoid duplicates
                if entity_text not in entities_by_type[entity_type]:
                    entities_by_type[entity_type].append(entity_text)

            logger.info(
                "NER extracted entities summary: %s",
                {label: len(values) for label, values in entities_by_type.items()},
            )
            logger.info(
                    "NER extracted entity values: %s",
                    entities_by_type,
                )
            return entities_by_type
        except Exception as e:
            logger.warning(f"Entity extraction failed: {e}")
            return {}

    def _split_text_into_segments(
        self, text: str, max_chars_per_segment: int
    ) -> List[str]:
        """
        Split text into segments for processing long documents

        Args:
            text: Text to split
            max_chars_per_segment: Maximum characters per segment

        Returns:
            List of text segments
        """
        segments = []
        start = 0

        while start < len(text):
            end = min(start + max_chars_per_segment, len(text))

            # Try to break at sentence boundaries
            if end < len(text):
                # Look for sentence endings near the end
                sentence_endings = [". ", "! ", "? ", "\n\n"]
                break_pos = end

                for ending in sentence_endings:
                    pos = text.rfind(ending, start, end)
                    if pos != -1 and pos > start + max_chars_per_segment // 2:
                        break_pos = pos + len(ending)
                        break

                end = break_pos

            segments.append(text[start:end])
            start = end

        return segments
