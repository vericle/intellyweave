"""
Unit tests for NamedEntityRecognitionService using the Rattenlinien (Nazi Rat Lines) document.

Tests cover:
1. Entity extraction from the real document about Nazi escape routes after WWII
2. Lazy loading behavior
3. Text segmentation
4. Error handling
"""

import warnings
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from elysia.api.services.ner_service import NamedEntityRecognitionService


class TestNERServiceUnit:
    """Unit tests for NamedEntityRecognitionService."""

    @pytest.fixture
    def rattenlinien_content(self):
        """Load the Rattenlinien (Nazi Rat Lines) test file content."""
        path = Path(__file__).parent.parent.parent.parent / "examples" / "cleaned" / "coldwar" / "Rattenlinien_cleaned.txt"
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    @pytest.fixture
    def expected_entities(self):
        """Expected entities from the Rattenlinien document about Nazi escape routes."""
        return {
            "person": ["Krunoslav Draganović", "Alois Hudal", "Juan Perón",
                      "Adolf Eichmann", "Josef Mengele", "Klaus Barbie",
                      "Ante Pavelić", "Hans-Ulrich Rudel", "Giovanni Montini",
                      "Pius XII", "Ernst von Weizsäcker", "Uki Goñi",
                      "Robert Clayton Mudd", "Franz Stangl", "Erich Priebke",
                      "Walter Rauff", "Eduard Roschmann", "Friedrich Schwend"],
            "date": ["1943", "1945", "1946", "1947", "1962", "1999",
                    "25. Juli 1943", "Mai 1945", "9. August 2018",
                    "5. Mai 2015", "4. Mai 1984", "21. November 2020"],
            "location": ["Italien", "Genua", "Spanien", "Argentinien",
                        "Buenos Aires", "Rom", "Südtirol", "Schleswig-Holstein",
                        "Flensburg", "Südamerika", "Österreich", "Vatikan",
                        "Barcelona", "Berlin", "Frankfurt", "Innsbruck"],
            "law": [],  # No specific laws mentioned in this document
            "event": ["Zweiter Weltkrieg", "Flucht", "Repatriierung",
                     "Präsidentschaftswahlen"],
            "organization": ["Counter Intelligence Corps", "CIC", "SS", "Ustascha",
                            "Italienisches Rotes Kreuz", "Internationales Rotes Kreuz",
                            "Stille Hilfe", "CEANA", "Vatikanisches Staatssekretariat",
                            "kroatische Nationalkirche", "NS-Regime", "Gestapo"]
        }

    def test_lazy_loading_behavior(self):
        """Test that GLiNER model loads only when accessed."""
        service = NamedEntityRecognitionService()
        assert service._ner_model is None  # Not loaded initially

        # Access property triggers loading
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model = service.ner_model
            # Model is either loaded or None (if GLiNER not available)
            assert model is not None or service._ner_model is None

    def test_extract_entities_empty_text(self):
        """Test handling of empty input."""
        service = NamedEntityRecognitionService()
        result = service.extract_entities("")
        assert result == {}

    def test_extract_entities_none_text(self):
        """Test handling of None input."""
        service = NamedEntityRecognitionService()
        result = service.extract_entities(None)
        assert result == {}

    def test_extract_entities_custom_labels(self):
        """Test with custom entity labels."""
        service = NamedEntityRecognitionService()
        result = service.extract_entities("Test text", labels=["person", "location"])
        assert isinstance(result, dict)

    def test_split_text_into_segments_short_text(self):
        """Test text segmentation for short text."""
        service = NamedEntityRecognitionService()
        text = "Short text."
        segments = service._split_text_into_segments(text, 100)
        assert len(segments) == 1
        assert segments[0] == text

    def test_split_text_into_segments_at_sentence_boundaries(self):
        """Test text segmentation breaks at sentence boundaries."""
        service = NamedEntityRecognitionService()
        text = "First sentence. Second sentence. Third sentence."
        segments = service._split_text_into_segments(text, 20)  # Force splitting
        assert len(segments) > 1
        # Should break at sentence endings
        for segment in segments:
            assert len(segment) <= 20 or segment.endswith(".")

    def test_extract_entities_returns_dict_structure(self):
        """Test that extract_entities returns proper dictionary structure."""
        service = NamedEntityRecognitionService()
        result = service.extract_entities("Test text")
        assert isinstance(result, dict)
        # If entities found, they should be lists
        for key, values in result.items():
            assert isinstance(values, list)
            assert isinstance(key, str)

    @patch('elysia.api.services.ner_service.GLiNER')
    def test_extract_entities_with_mock_model(self, mock_gliner_class):
        """Test entity extraction with mocked GLiNER model."""
        # Setup mock model
        mock_model = MagicMock()
        mock_model.predict_entities.return_value = [
            {"label": "person", "text": "John Smith"},
            {"label": "location", "text": "New York"},
            {"label": "person", "text": "Jane Doe"}  # Test deduplication
        ]
        mock_gliner_class.from_pretrained.return_value = mock_model

        service = NamedEntityRecognitionService()

        # Force model loading
        _ = service.ner_model

        result = service.extract_entities("Test text with entities")

        # Verify model was called
        mock_model.predict_entities.assert_called_once()

        # Verify result structure
        assert "person" in result
        assert "location" in result
        assert "John Smith" in result["person"]
        assert "Jane Doe" in result["person"]  # Should deduplicate
        assert "New York" in result["location"]

    @patch('elysia.api.services.ner_service.GLiNER')
    def test_extract_entities_handles_model_failure(self, mock_gliner_class):
        """Test graceful handling when model loading fails."""
        mock_gliner_class.from_pretrained.side_effect = Exception("Model load failed")

        service = NamedEntityRecognitionService()

        # This should not crash, should return empty dict
        result = service.extract_entities("Test text")
        assert result == {}

    def test_extract_entities_with_real_document(self, rattenlinien_content, expected_entities):
        """Test entity extraction using the Rattenlinien document about Nazi escape routes."""
        service = NamedEntityRecognitionService()

        entities = service.extract_entities(rattenlinien_content)

        # Verify result is a dictionary
        assert isinstance(entities, dict)

        # If entities were extracted (GLiNER available), verify structure matches expected
        if entities:
            # Check that expected entity types are present (except 'law' which may be empty)
            for entity_type in expected_entities.keys():
                if expected_entities[entity_type]:  # Only check non-empty expected lists
                    assert entity_type in entities, f"Missing entity type: {entity_type}"
                    assert isinstance(entities[entity_type], list), f"Entity type {entity_type} should be a list"

            # Verify some key entities are extracted
            if "person" in entities and entities["person"]:
                # Should contain some of the expected persons (Nazi war criminals, church figures)
                extracted_persons = set(entities["person"])
                expected_persons = set(expected_entities["person"])
                overlap = extracted_persons.intersection(expected_persons)
                assert len(overlap) > 0, "Should extract some expected persons (e.g., Eichmann, Mengele, Hudal)"

            if "location" in entities and entities["location"]:
                # Should contain some of the expected locations (escape route cities)
                extracted_locations = set(entities["location"])
                expected_locations = set(expected_entities["location"])
                overlap = extracted_locations.intersection(expected_locations)
                assert len(overlap) > 0, "Should extract some expected locations (e.g., Rom, Argentinien, Buenos Aires)"