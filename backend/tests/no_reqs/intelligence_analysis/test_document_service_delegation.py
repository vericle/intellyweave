"""
Unit tests for DocumentService delegation to NER and Geocoding services.

Tests cover:
1. Delegation to NamedEntityRecognitionService
2. Delegation to GeocodingService
3. Error propagation from services
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from pathlib import Path

from elysia.api.services.document import DocumentService
from elysia.config import Settings


class TestDocumentServiceDelegation:
    """Unit tests for DocumentService delegation pattern."""

    @pytest.fixture
    def document_service(self):
        """Create DocumentService instance."""
        return DocumentService(None)

    @pytest.fixture
    def mock_ner_service(self):
        """Create mock NER service with Rattenlinien entities."""
        mock_ner = MagicMock()
        mock_ner.extract_entities.return_value = {
            "person": ["Adolf Eichmann", "Josef Mengele", "Alois Hudal"],
            "location": ["Rom", "Buenos Aires", "Argentinien"]
        }
        return mock_ner

    @pytest.fixture
    def mock_geocoding_service(self):
        """Create mock geocoding service with Rattenlinien locations."""
        mock_geo = AsyncMock()
        mock_geo.enrich_locations_batch.return_value = [
            {"locationName": "Rome, Italy", "country": "Italy"}
        ]
        mock_geo.geocode_locations_batch.return_value = [
            {"locationName": "Rome, Italy", "coordinates": [12.4964, 41.9028]}
        ]
        mock_geo.geocode_location.return_value = {
            "lat": 41.9028, "lon": 12.4964, "place_name": "Rome, Italy"
        }
        return mock_geo

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings."""
        return MagicMock(spec=Settings)

    def test_document_service_initializes_services(self, document_service):
        """Test that DocumentService initializes the required services."""
        assert hasattr(document_service, 'ner_service')
        assert hasattr(document_service, 'geocoding_service')
        assert document_service.ner_service is not None
        assert document_service.geocoding_service is not None

    def test_extract_entities_delegates_to_ner_service(self, document_service, mock_ner_service):
        """Test that _extract_entities delegates to NER service."""
        # Replace the service with mock
        document_service.ner_service = mock_ner_service

        test_text = "Adolf Eichmann fled to Argentina via the Vatican ratlines."
        result = document_service._extract_entities(test_text)

        # Verify delegation occurred
        mock_ner_service.extract_entities.assert_called_once_with(test_text, None)
        assert result == mock_ner_service.extract_entities.return_value

    def test_extract_entities_delegates_with_custom_labels(self, document_service, mock_ner_service):
        """Test that _extract_entities delegates with custom labels."""
        document_service.ner_service = mock_ner_service

        custom_labels = ["person", "location"]
        result = document_service._extract_entities("Test text", labels=custom_labels)

        mock_ner_service.extract_entities.assert_called_once_with("Test text", custom_labels)
        assert result == mock_ner_service.extract_entities.return_value

    @pytest.mark.asyncio
    async def test_enrich_locations_batch_delegates(self, document_service, mock_geocoding_service, mock_settings):
        """Test that _enrich_locations_batch delegates to geocoding service."""
        document_service.geocoding_service = mock_geocoding_service

        locations = ["Rom", "Buenos Aires"]
        chunk_content = "Nazi escape routes through Italy to South America"

        result = await document_service._enrich_locations_batch(locations, mock_settings, chunk_content)

        mock_geocoding_service.enrich_locations_batch.assert_called_once_with(
            locations, mock_settings, chunk_content
        )
        assert result == mock_geocoding_service.enrich_locations_batch.return_value

    @pytest.mark.asyncio
    async def test_geocode_locations_batch_delegates(self, document_service, mock_geocoding_service):
        """Test that _geocode_locations_batch delegates to geocoding service."""
        document_service.geocoding_service = mock_geocoding_service

        enriched_locations = [{"locationName": "Rome, Italy"}]
        mapbox_token = "fake_token"

        result = await document_service._geocode_locations_batch(enriched_locations, mapbox_token)

        mock_geocoding_service.geocode_locations_batch.assert_called_once_with(
            enriched_locations, mapbox_token
        )
        assert result == mock_geocoding_service.geocode_locations_batch.return_value

    @pytest.mark.asyncio
    async def test_geocode_location_delegates(self, document_service, mock_geocoding_service):
        """Test that _geocode_location delegates to geocoding service (async)."""
        document_service.geocoding_service = mock_geocoding_service

        result = await document_service._geocode_location("Rom")

        mock_geocoding_service.geocode_location.assert_called_once_with("Rom")
        assert result == mock_geocoding_service.geocode_location.return_value

    def test_extract_entities_propagates_ner_errors(self, document_service, mock_ner_service):
        """Test that NER service errors are propagated."""
        document_service.ner_service = mock_ner_service
        mock_ner_service.extract_entities.side_effect = Exception("NER error")

        with pytest.raises(Exception, match="NER error"):
            document_service._extract_entities("Test text")

    @pytest.mark.asyncio
    async def test_enrich_locations_propagates_geocoding_errors(self, document_service, mock_geocoding_service, mock_settings):
        """Test that geocoding service errors are propagated."""
        document_service.geocoding_service = mock_geocoding_service
        mock_geocoding_service.enrich_locations_batch.side_effect = Exception("Geocoding error")

        with pytest.raises(Exception, match="Geocoding error"):
            await document_service._enrich_locations_batch(["Rom"], mock_settings)

    @pytest.mark.asyncio
    async def test_geocode_locations_propagates_geocoding_errors(self, document_service, mock_geocoding_service):
        """Test that geocoding service errors are propagated."""
        document_service.geocoding_service = mock_geocoding_service
        mock_geocoding_service.geocode_locations_batch.side_effect = Exception("Geocoding error")

        with pytest.raises(Exception, match="Geocoding error"):
            await document_service._geocode_locations_batch([{"locationName": "Rom"}], "token")

    def test_delegation_preserves_method_signatures(self, document_service):
        """Test that delegation methods preserve expected signatures."""
        import inspect

        # Check _extract_entities signature
        sig = inspect.signature(document_service._extract_entities)
        params = list(sig.parameters.keys())
        assert 'text' in params
        assert 'labels' in params

        # Check _enrich_locations_batch signature
        sig = inspect.signature(document_service._enrich_locations_batch)
        params = list(sig.parameters.keys())
        assert 'locations' in params
        assert 'settings' in params
        assert 'chunk_content' in params

        # Check _geocode_locations_batch signature
        sig = inspect.signature(document_service._geocode_locations_batch)
        params = list(sig.parameters.keys())
        assert 'enriched_locations' in params
        assert 'mapbox_token' in params

        # Check _geocode_location signature
        sig = inspect.signature(document_service._geocode_location)
        params = list(sig.parameters.keys())
        assert 'location_name' in params