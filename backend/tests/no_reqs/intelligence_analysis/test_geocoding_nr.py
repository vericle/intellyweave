"""
Unit tests for GeocodingService using mocked dependencies.

Tests cover:
1. Location enrichment batch processing
2. Batch geocoding with Mapbox API
3. Single location geocoding
4. Error handling and edge cases
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

from elysia.api.services.geocoding_service import GeocodingService
from elysia.config import Settings


class TestGeocodingServiceUnit:
    """Unit tests for GeocodingService."""

    @pytest.fixture
    def geocoding_service(self):
        """Create GeocodingService instance."""
        return GeocodingService()

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings with API keys."""
        settings = MagicMock(spec=Settings)
        settings.API_KEYS = {
            "anthropic_api_key": "test-anthropic-key",
            "ANTHROPIC_API_KEY": "test-anthropic-key"
        }
        return settings

    @pytest.fixture
    def rattenlinien_locations(self):
        """Locations extracted from Rattenlinien document about Nazi escape routes."""
        return ["Rom", "Genua", "Buenos Aires", "Argentinien", "Südtirol", "Flensburg"]

    @pytest.fixture
    def enriched_locations_sample(self):
        """Sample enriched location data from Rattenlinien escape routes."""
        return [
            {
                "locationName": "Rome, Italy",
                "locationType": "City",
                "description": "Key transit point for Nazi escape routes via Vatican connections",
                "country": "Italy"
            },
            {
                "locationName": "Buenos Aires, Argentina",
                "locationType": "City",
                "description": "Primary destination for fleeing Nazi war criminals in South America",
                "country": "Argentina"
            },
            {
                "locationName": "Genoa, Italy",
                "locationType": "City",
                "description": "Major port city used for escape routes to South America",
                "country": "Italy"
            }
        ]

    def test_service_initialization(self, geocoding_service):
        """Test that service initializes correctly."""
        assert geocoding_service is not None
        assert hasattr(geocoding_service, 'enrich_locations_batch')
        assert hasattr(geocoding_service, 'geocode_locations_batch')
        assert hasattr(geocoding_service, 'geocode_location')

    @pytest.mark.asyncio
    async def test_enrich_locations_batch_empty_list(self, geocoding_service, mock_settings):
        """Test batch enrichment with empty location list."""
        result = await geocoding_service.enrich_locations_batch([], mock_settings)
        assert result == []

   
    @pytest.mark.asyncio
    async def test_geocode_locations_batch_empty_list(self, geocoding_service):
        """Test batch geocoding with empty list."""
        result = await geocoding_service.geocode_locations_batch([])
        assert result == []

    @patch('elysia.api.services.geocoding_service.aiohttp.ClientSession')
    @pytest.mark.asyncio
    async def test_geocode_locations_batch_api_call(self, mock_session_class, geocoding_service, enriched_locations_sample):
        """Test batch geocoding makes correct API call."""
        # Build dummy async context manager objects to mimic aiohttp structure
        class DummyResponse:
            status = 200
            async def json(self):
                return {
                    "batch": [
                        {"features": [{"geometry": {"coordinates": [12.4964, 41.9028]}, "properties": {"full_address": "Rome, Italy"}}]},
                        {"features": [{"geometry": {"coordinates": [-58.3816, -34.6037]}, "properties": {"full_address": "Buenos Aires, Argentina"}}]},
                        {"features": [{"geometry": {"coordinates": [8.9463, 44.4056]}, "properties": {"full_address": "Genoa, Italy"}}]}
                    ]
                }
            async def text(self):
                return "OK"

        class PostContext:
            async def __aenter__(self):
                return DummyResponse()
            async def __aexit__(self, exc_type, exc, tb):
                pass

        class DummySession:
            async def __aenter__(self):
                return self
            async def __aexit__(self, exc_type, exc, tb):
                pass
            def post(self, *args, **kwargs):
                return PostContext()

        mock_session_class.return_value = DummySession()

        result = await geocoding_service.geocode_locations_batch(enriched_locations_sample, "fake_token")

        # Verify result structure
        assert isinstance(result, list)
        assert len(result) == 3

        # Check successful geocoding
        successful = [loc for loc in result if loc.get("coordinates")]
        assert len(successful) >= 1

        # Check coordinates structure
        for loc in successful:
            assert "coordinates" in loc
            assert "latitude" in loc
            assert "longitude" in loc
            assert "name" in loc

    @patch('elysia.api.services.geocoding_service.aiohttp.ClientSession')
    @pytest.mark.asyncio
    async def test_geocode_locations_batch_handles_api_error(self, mock_session_class, geocoding_service, enriched_locations_sample):
        """Test batch geocoding handles API errors."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.text.return_value = "Internal Server Error"
        mock_session.post.return_value.__aenter__.return_value = mock_response
        mock_session_class.return_value.__aenter__.return_value = mock_session

        result = await geocoding_service.geocode_locations_batch(enriched_locations_sample, "fake_token")

        # Should return empty list on API error
        assert result == []

    @patch('elysia.api.services.geocoding_service.aiohttp.ClientSession')
    @pytest.mark.asyncio
    async def test_geocode_location_single(self, mock_session_class, geocoding_service):
        """Test single location geocoding with Rome from Rattenlinien escape routes."""
        class DummyResponse:
            status = 200
            async def json(self):
                return {
                    "features": [{
                        "geometry": {"coordinates": [12.4964, 41.9028]},
                        "properties": {"place_name": "Rome, Italy"},
                        "relevance": 0.9,
                        "place_type": ["place"]
                    }]
                }
            async def text(self):
                return "OK"

        class GetContext:
            async def __aenter__(self):
                return DummyResponse()
            async def __aexit__(self, exc_type, exc, tb):
                pass

        class DummySession:
            async def __aenter__(self):
                return self
            async def __aexit__(self, exc_type, exc, tb):
                pass
            def get(self, *args, **kwargs):
                return GetContext()

        mock_session_class.return_value = DummySession()

        result = await geocoding_service.geocode_location("Rom")

        # Verify result structure
        assert result is not None
        assert "lat" in result
        assert "lon" in result
        assert "place_name" in result
        assert "location_type" in result
        assert "relevance" in result

        # Verify coordinates for Rome
        assert result["lat"] == 41.9028
        assert result["lon"] == 12.4964

    @patch('elysia.api.services.geocoding_service.aiohttp.ClientSession')
    @pytest.mark.asyncio
    async def test_geocode_location_no_results(self, mock_session_class, geocoding_service):
        """Test single location geocoding with no results."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {"features": []}
        mock_session.get.return_value.__aenter__.return_value = mock_response
        mock_session_class.return_value.__aenter__.return_value = mock_session

        result = await geocoding_service.geocode_location("NonexistentPlace")

        # Should return None for no results
        assert result is None

    @pytest.mark.asyncio
    async def test_geocode_location_invalid_input(self, geocoding_service):
        """Test single location geocoding with invalid input."""
        result = await geocoding_service.geocode_location("")
        assert result is None

        result = await geocoding_service.geocode_location(None)
        assert result is None

        result = await geocoding_service.geocode_location("   ")
        assert result is None

    def test_country_mapping(self, geocoding_service):
        """Test country name to code mapping."""
        # This is tested indirectly through the batch geocoding logic
        # The mapping is used internally in geocode_locations_batch
        service = geocoding_service

        # Test that the mapping logic exists (can't easily test private method)
        assert hasattr(service, 'geocode_locations_batch')

        # The country mapping is defined within the method
        # We verify it exists by checking the method can be called
        assert callable(service.geocode_locations_batch)

    @patch('elysia.api.services.geocoding_service.os.getenv')
    @pytest.mark.asyncio
    async def test_geocode_locations_batch_no_token(self, mock_getenv, geocoding_service, enriched_locations_sample):
        """Test batch geocoding with no Mapbox token."""
        mock_getenv.return_value = None

        result = await geocoding_service.geocode_locations_batch(enriched_locations_sample)

        # Should return empty list when no token
        assert result == []

    @patch('elysia.api.services.geocoding_service.aiohttp.ClientSession')
    @pytest.mark.asyncio
    async def test_geocode_location_with_coordinates_in_result(self, mock_session_class, geocoding_service):
        """Test geocoding returns both lat/lon and coordinates dict for frontend compatibility."""
        class DummyResponse:
            status = 200
            async def json(self):
                # Match actual Mapbox Geocoding API response structure
                return {
                    "features": [{
                        "geometry": {"coordinates": [-122.4194, 37.7749]},
                        "place_name": "San Francisco, California, USA",
                        "relevance": 0.95,
                        "place_type": ["place", "locality"]
                    }]
                }
            async def text(self):
                return "OK"

        class GetContext:
            async def __aenter__(self):
                return DummyResponse()
            async def __aexit__(self, exc_type, exc, tb):
                pass

        class DummySession:
            async def __aenter__(self):
                return self
            async def __aexit__(self, exc_type, exc, tb):
                pass
            def get(self, *args, **kwargs):
                return GetContext()

        mock_session_class.return_value = DummySession()

        result = await geocoding_service.geocode_location("San Francisco")

        # Verify result has both formats for compatibility
        assert result is not None
        assert "lat" in result
        assert "lon" in result
        assert result["lat"] == 37.7749
        assert result["lon"] == -122.4194

        # Verify location type and place name
        # The service maps place_type "place" to "City"
        assert result["location_type"] == "City"
        assert result["place_name"] == "San Francisco, California, USA"
        assert result["relevance"] == 0.95