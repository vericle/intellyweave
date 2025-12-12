"""
Integration tests for geocoding functionality using the Rattenlinien (Nazi Rat Lines) document.

Tests cover:
1. Batch geocoding with Mapbox API
2. Location enrichment with LLM
3. Performance validation
4. Error handling

Uses locations from Nazi escape routes document (Rome, Genoa, Buenos Aires, etc.)

Requires:
- MAPBOX_ACCESS_TOKEN environment variable
- ANTHROPIC_API_KEY for enrichment (optional)
"""

import pytest
import os
from pathlib import Path

from elysia.api.services.document import DocumentService
from elysia.api.services.geocoding_service import GeocodingService
from elysia.config import Settings


@pytest.mark.asyncio
class TestGeocodingIntegration:
    """Integration tests for geocoding using real Rattenlinien escape route data."""

    @pytest.fixture
    def rattenlinien_path(self):
        """Path to the Rattenlinien test file."""
        return Path(__file__).parent.parent.parent.parent / "examples" / "cleaned" / "coldwar" / "Rattenlinien_cleaned.txt"

    async def test_batch_geocoding_with_real_locations(self):
        """Test batch geocoding with locations from Rattenlinien escape routes document."""
        if not os.getenv("MAPBOX_ACCESS_TOKEN"):
            pytest.skip("MAPBOX_ACCESS_TOKEN not set")

        service = DocumentService(None)

        # Locations from Nazi escape routes (Rattenlinien)
        enriched_locations = [
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

        import time
        start_time = time.time()

        geocoded = await service._geocode_locations_batch(
            enriched_locations,
            os.getenv("MAPBOX_ACCESS_TOKEN")
        )

        duration = time.time() - start_time

        print(f"\n[PERFORMANCE] Batch geocoding: {duration:.2f}s for {len(enriched_locations)} locations")

        # Verify results
        assert isinstance(geocoded, list)
        assert len(geocoded) == len(enriched_locations)

        # Check that at least some geocoding succeeded
        successful_geocodes = [loc for loc in geocoded if loc.get("coordinates")]
        assert len(successful_geocodes) > 0, "At least one location should be geocoded successfully"

        # Verify coordinate structure
        for loc in successful_geocodes:
            assert "coordinates" in loc
            assert "latitude" in loc
            assert "longitude" in loc
            assert "name" in loc

            # Coordinates should be valid
            coords = loc["coordinates"]
            assert isinstance(coords, list)
            assert len(coords) == 2
            assert -180 <= coords[0] <= 180  # longitude
            assert -90 <= coords[1] <= 90    # latitude

    async def test_single_location_geocoding(self):
        """Test single location geocoding with Mapbox using Rome from Rattenlinien."""
        if not os.getenv("MAPBOX_ACCESS_TOKEN"):
            pytest.skip("MAPBOX_ACCESS_TOKEN not set")

        service = DocumentService(None)

        # Test geocoding "Rom" (Rome) - key transit point in Nazi escape routes
        result = await service._geocode_location("Rom")

        if result:  # May be None if API fails
            assert "lat" in result
            assert "lon" in result
            assert "place_name" in result
            assert "location_type" in result

            # Should be Rome coordinates (approximately)
            assert 41.8 < result["lat"] < 42.0  # Rome latitude
            assert 12.4 < result["lon"] < 12.6  # Rome longitude

    async def test_geocoding_with_country_filtering(self):
        """Test geocoding respects country filtering using Rattenlinien locations."""
        if not os.getenv("MAPBOX_ACCESS_TOKEN"):
            pytest.skip("MAPBOX_ACCESS_TOKEN not set")

        service = DocumentService(None)

        # Test with country-specific location from Nazi escape routes
        enriched_locations = [
            {
                "locationName": "Barcelona",
                "locationType": "City",
                "description": "City in Spain used as transit point for Nazi escape routes",
                "country": "Spain"
            }
        ]

        geocoded = await service._geocode_locations_batch(
            enriched_locations,
            os.getenv("MAPBOX_ACCESS_TOKEN")
        )

        assert len(geocoded) == 1
        if geocoded[0].get("coordinates"):
            # Should geocode to Barcelona, Spain
            coords = geocoded[0]["coordinates"]
            # Barcelona coordinates approximately
            assert 41.3 < coords[1] < 41.5  # latitude
            assert 2.1 < coords[0] < 2.3    # longitude

    async def test_batch_geocoding_error_handling(self):
        """Test batch geocoding handles API errors gracefully."""
        service = DocumentService(None)

        enriched_locations = [
            {"locationName": "Valid Location", "country": "Austria"},
            {"locationName": "", "country": "Austria"},  # Invalid
        ]

        # Test without token (should return empty)
        geocoded = await service._geocode_locations_batch(enriched_locations, None)
        assert geocoded == []

        # Test with invalid token (should handle gracefully)
        geocoded = await service._geocode_locations_batch(enriched_locations, "invalid_token")
        # May return empty or partial results depending on API behavior
        assert isinstance(geocoded, list)

    async def test_location_enrichment_with_context(self, rattenlinien_path):
        """Test location enrichment uses document context from Rattenlinien."""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")

        if not rattenlinien_path.exists():
            pytest.skip(f"Test document not found at {rattenlinien_path}")

        service = DocumentService(None)

        # Locations from Rattenlinien that need historical context
        locations = ["Sonderbereich Mürwik", "Südtirol"]

        # Load document content for context
        with open(rattenlinien_path, 'r', encoding='utf-8') as f:
            chunk_content = f.read()[:1000]

        settings = Settings()

        enriched = await service._enrich_locations_batch(locations, settings, chunk_content)

        assert len(enriched) == len(locations)

        # Verify enrichment used context
        for loc in enriched:
            assert "locationName" in loc
            # Should have proper location names
            assert "locationName" in loc
            assert "country" in loc

    async def test_geocoding_performance_metrics(self):
        """Test geocoding performance meets expectations using Rattenlinien locations."""
        if not os.getenv("MAPBOX_ACCESS_TOKEN"):
            pytest.skip("MAPBOX_ACCESS_TOKEN not set")

        service = DocumentService(None)

        # Test with multiple locations from Nazi escape routes
        locations = [
            {"locationName": "Rom", "country": "Italy"},
            {"locationName": "Genua", "country": "Italy"},
            {"locationName": "Buenos Aires", "country": "Argentina"},
            {"locationName": "Barcelona", "country": "Spain"},
            {"locationName": "Flensburg", "country": "Germany"}
        ]

        import time
        start_time = time.time()

        geocoded = await service._geocode_locations_batch(
            locations,
            os.getenv("MAPBOX_ACCESS_TOKEN")
        )

        duration = time.time() - start_time

        print(f"\n[PERFORMANCE] Geocoded {len(locations)} locations in {duration:.2f}s")
        print(f"[PERFORMANCE] Average: {duration/len(locations):.3f}s per location")

        # Performance expectations (batch should be fast)
        assert duration < 10, f"Batch geocoding too slow: {duration:.2f}s"

        # Success rate
        successful = sum(1 for loc in geocoded if loc.get("coordinates"))
        success_rate = successful / len(locations)
        print(f"[PERFORMANCE] Success rate: {success_rate:.1%}")

        assert success_rate > 0.6, f"Success rate too low: {success_rate:.1%}"

    async def test_enrich_locations_batch_filters_invalid_integration(self):
        """Integration: enrichment filters invalid entries using real LLM (requires ANTHROPIC_API_KEY)."""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")

        service = GeocodingService()
        settings = Settings()
        locations = ["", "   ", None, "Valid Location"]
        enriched = await service.enrich_locations_batch(locations, settings)
        # Only the valid non-empty unique location should be enriched
        assert len(enriched) <= 1
        if enriched:
            assert "locationName" in enriched[0]

    async def test_enrich_locations_batch_deduplicates_integration(self):
        """Integration: enrichment deduplicates locations using real LLM (requires ANTHROPIC_API_KEY)."""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")

        service = GeocodingService()
        settings = Settings()
        locations = ["Rom", "Rom", "Buenos Aires", "Rom"]
        enriched = await service.enrich_locations_batch(locations, settings)
        # Should process unique locations only (Rom, Buenos Aires)
        assert len(enriched) <= 2
        if enriched:
            for item in enriched:
                assert "locationName" in item

    async def test_enrich_locations_batch_calls_llm_integration(self):
        """Integration: verify LLM enrichment returns structured data (requires ANTHROPIC_API_KEY)."""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")

        service = GeocodingService()
        settings = Settings()
        locations = ["Rom", "Genua", "Buenos Aires"]
        enriched = await service.enrich_locations_batch(locations, settings)
        assert isinstance(enriched, list)
        assert len(enriched) >= 1
        first = enriched[0]
        assert "locationName" in first
        assert "locationType" in first
        assert "country" in first

    async def test_enrich_locations_batch_handles_llm_error_integration(self):
        """Integration: simulate LLM auth error with invalid API key."""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")

        service = GeocodingService()
        settings = Settings()
        # Force invalid key to trigger authentication exception
        settings.API_KEYS["anthropic_api_key"] = "invalid-key"
        settings.API_KEYS["ANTHROPIC_API_KEY"] = "invalid-key"
        with pytest.raises(Exception):
            await service.enrich_locations_batch(["Rom"], settings)

    async def test_geospatial_transformation_tool_with_virtual_documents(self):
        """
        Integration test for GeospatialTransformationTool with virtual document creation.

        Tests the complete workflow:
        1. Geocode missing location (Rome)
        2. Generate contextual description using conversation history
        3. Create virtual document via DocumentService
        4. Print all intermediate steps and results

        Requires:
        - MAPBOX_ACCESS_TOKEN for geocoding
        - ANTHROPIC_API_KEY for description generation
        - Weaviate instance for document persistence
        """
        if not os.getenv("MAPBOX_ACCESS_TOKEN"):
            pytest.skip("MAPBOX_ACCESS_TOKEN not set")
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")

        from elysia.agents.geo_transformer import GeospatialTransformationTool
        from elysia.util.client import ClientManager
        from elysia.tree.objects import TreeData, CollectionData, Atlas
        from elysia.config import Settings, load_base_lm, load_complex_lm
        import dspy

        print("\n" + "=" * 80)
        print("GEOSPATIAL TRANSFORMATION TOOL - VIRTUAL DOCUMENT CREATION TEST")
        print("=" * 80)

        # Initialize settings and models
        settings = Settings.from_env_vars()
        client_manager = ClientManager()
        base_lm = load_base_lm(settings)
        complex_lm = load_complex_lm(settings)

        # Initialize TreeData with conversation history
        collection_data = CollectionData(
            collection_names=["ELYSIA_CHUNKED_elysia_uploaded_documents__"],
            metadata={},
            logger=settings.logger
        )
        atlas = Atlas()

        # Create mock conversation history simulating intelligence analysis
        conversation_history = [
            # {
            #     "role": "user",
            #     "content": "What do you know about Cold War exfiltration routes from Austria?"
            # },
            # {
            #     "role": "assistant",
            #     "content": "The documents show that CIC operations coordinated defector exfiltration from Vienna and Salzburg to Rome, then to South America (Peru, Brazil)."
            # },
            # {
            #     "role": "user",
            #     "content": "Can you provide more details about the Rome safe house operations?"
            # },
            # {
            #     "role": "assistant",
            #     "content": "Rome served as a critical waypoint in the ratline, where defectors were processed before final relocation to South America."
            # },
            # {
            #     "role": "user",
            #     "content": "Please geocode and persist the geolocation of Rome in Italy as it's mentioned frequently but not in the database"
            # }
        ]

        tree_data = TreeData(
            collection_data=collection_data,
            atlas=atlas,
            settings=settings,
            conversation_history=conversation_history,
            user_prompt="Check if Frankfurt and Mainz is available in the database and if not, geocode it and save it to the database"
        )

        print(f"\n[SETUP] Conversation History: {len(conversation_history)} messages")
        print(f"[SETUP] User Prompt: {tree_data.user_prompt}")
        print(f"[SETUP] Base LM: {settings.BASE_MODEL}")
        print(f"[SETUP] Complex LM: {settings.COMPLEX_MODEL}")

        # Initialize GeospatialTransformationTool
        tool = GeospatialTransformationTool(logger=settings.logger)

        print(f"\n[TOOL] Initialized: {tool.name}")
        print(f"[TOOL] Description: {tool.description}")

        # Create mock entity for Rome (missing coordinates)
        mock_entities = [
            {
                "name": "Frankfurt",
                "type": "location",
                "description": "Frankfurt is a city in Germany.",
            }
        ]

        print(f"\n[INPUT] Entities: {len(mock_entities)}")
        print(f"[INPUT] Entity: {mock_entities[0]}")

        # Test inputs with persist_missing_locations=True
        inputs = {
            "entities": mock_entities,
            "user_interest": tree_data.user_prompt,
            "persist_missing_locations": True,
            "user_id": "test_geotransformer_user"
        }

        print(f"\n[INPUT] User Interest: {inputs['user_interest']}")
        print(f"[INPUT] Persist Missing: {inputs['persist_missing_locations']}")
        print(f"[INPUT] User ID: {inputs['user_id']}")

        print("\n" + "-" * 80)
        print("EXECUTING GEOSPATIAL TRANSFORMATION TOOL")
        print("-" * 80)

        step_counter = 0
        enriched_result = None

        try:
            # Execute the tool
            async for result in tool(
                tree_data=tree_data,
                inputs=inputs,
                base_lm=base_lm,
                complex_lm=complex_lm,
                client_manager=client_manager,
                settings=settings
            ):
                result_type = type(result).__name__

                print(f"\n[STEP {step_counter}] Type: {result_type}")

                if result_type == "Status":
                    print(f"[STEP {step_counter}] Message: {result.text}")

                elif result_type == "Error":
                    print(f"[STEP {step_counter}] ERROR: {result.text}")

                elif result_type == "Result":
                    print(f"[STEP {step_counter}] Result Name: {result.name}")
                    print(f"[STEP {step_counter}] Metadata: {result.metadata}")

                    if result.objects:
                        print(f"[STEP {step_counter}] Objects Count: {len(result.objects)}")
                        for i, obj in enumerate(result.objects):
                            print(f"\n[STEP {step_counter}] Object {i}:")
                            print(f"  - Name: {obj.get('name')}")
                            print(f"  - Type: {obj.get('type')}")
                            print(f"  - Coordinates: {obj.get('coordinates')}")
                            print(f"  - Latitude: {obj.get('latitude')}")
                            print(f"  - Longitude: {obj.get('longitude')}")
                            print(f"  - Location Type: {obj.get('location_type')}")
                            print(f"  - Is Enriched: {obj.get('is_enriched')}")
                            print(f"  - Enrichment Source: {obj.get('enrichment_source')}")

                    enriched_result = result

                step_counter += 1

            print("\n" + "=" * 80)
            print(f"✓ GeospatialTransformationTool completed successfully")
            print(f"✓ Total steps: {step_counter}")

            if enriched_result:
                metadata = enriched_result.metadata
                print(f"\n[SUMMARY] Original Count: {metadata.get('original_count')}")
                print(f"[SUMMARY] Enriched Count: {metadata.get('enriched_count')}")
                print(f"[SUMMARY] Persisted Count: {metadata.get('persisted_count')}")

            print("=" * 80)

        except Exception as e:
            print(f"\n✗ Error during execution:")
            print(f"  Error Type: {type(e).__name__}")
            print(f"  Error Message: {str(e)}")
            import traceback
            print(f"\nTraceback:")
            print(traceback.format_exc())
            raise

        finally:
            await client_manager.close_clients()
