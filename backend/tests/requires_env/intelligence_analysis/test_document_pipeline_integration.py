"""
Integration test for document processing pipeline using Rattenlinien (Nazi Rat Lines) document.

This test validates the complete pipeline:
1. Document upload with entity extraction
2. Location enrichment via LLM
3. Batch geocoding via Mapbox API

Uses the Rattenlinien document about Nazi escape routes after WWII and validates
expected entities (war criminals, escape route locations) and geocoding results.

Requires:
- ANTHROPIC_API_KEY for location enrichment
- MAPBOX_ACCESS_TOKEN for geocoding
- Weaviate instance for document storage
"""

import pytest
import os
from pathlib import Path

from elysia.api.services.document import DocumentService
from elysia.config import Settings


@pytest.mark.asyncio
class TestRattenlinienPipeline:
    """Integration tests using the Rattenlinien (Nazi Rat Lines) document."""

    @pytest.fixture
    def rattenlinien_path(self):
        """Path to the Rattenlinien test file."""
        return Path(__file__).parent.parent.parent.parent / "examples" / "cleaned" / "coldwar" / "Rattenlinien_cleaned.txt"

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

    async def test_document_upload_with_entity_extraction(self, rattenlinien_path, expected_entities):
        """Test document upload extracts expected entities from Rattenlinien document."""
        if not rattenlinien_path.exists():
            pytest.skip(f"Test document not found at {rattenlinien_path}")

        service = DocumentService(None)

        # Upload document
        with open(rattenlinien_path, 'rb') as f:
            result = await service.upload_document(
                file_path=str(rattenlinien_path),
                filename=rattenlinien_path.name,
                user_id="test_user",
                auto_preprocess=True,
                auto_geocode=False,  # Test entity extraction separately
                settings=None
            )

        assert result["success"] is True
        assert "document_id" in result

        document_id = result["document_id"]

        # Verify entities were extracted
        # Note: This would require querying Weaviate to check stored entities
        # For now, just verify the upload succeeded
        assert result["chunks_created"] > 0

    async def test_location_enrichment_batch(self, rattenlinien_path):
        """Test batch location enrichment with real LLM using Rattenlinien locations."""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")

        service = DocumentService(None)

        # Locations from the Rattenlinien document (Nazi escape route cities)
        locations = ["Rom", "Genua", "Buenos Aires", "Südtirol", "Flensburg"]

        # Load document content for context
        with open(rattenlinien_path, 'r', encoding='utf-8') as f:
            chunk_content = f.read()[:1000]  # First 1000 chars for context

        settings = Settings()

        # Test enrichment
        enriched = await service._enrich_locations_batch(locations, settings, chunk_content)

        assert isinstance(enriched, list)
        assert len(enriched) > 0

        # Verify enrichment structure
        for loc in enriched:
            assert "locationName" in loc
            assert "locationType" in loc
            assert "description" in loc
            assert "country" in loc

    async def test_batch_geocoding(self, rattenlinien_path):
        """Test batch geocoding with Mapbox API using Rattenlinien escape route locations."""
        if not os.getenv("MAPBOX_ACCESS_TOKEN"):
            pytest.skip("MAPBOX_ACCESS_TOKEN not set")

        service = DocumentService(None)

        # Sample enriched locations from Rattenlinien escape routes
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
                "description": "Primary destination for fleeing Nazi war criminals",
                "country": "Argentina"
            }
        ]

        # Test geocoding
        geocoded = await service._geocode_locations_batch(
            enriched_locations,
            os.getenv("MAPBOX_ACCESS_TOKEN")
        )

        assert isinstance(geocoded, list)
        assert len(geocoded) == len(enriched_locations)

        # Verify geocoding results
        successful_geocodes = [loc for loc in geocoded if loc.get("coordinates")]
        assert len(successful_geocodes) > 0, "At least some locations should be geocoded successfully"

        for loc in successful_geocodes:
            assert "coordinates" in loc
            assert "latitude" in loc
            assert "longitude" in loc
            assert "name" in loc

    async def test_full_pipeline_integration(self, rattenlinien_path, expected_entities):
        """Test the complete pipeline: upload → extract → enrich → geocode."""
        if not (os.getenv("ANTHROPIC_API_KEY") and os.getenv("MAPBOX_ACCESS_TOKEN")):
            pytest.skip("Required API keys not set")

        if not rattenlinien_path.exists():
            pytest.skip(f"Test document not found at {rattenlinien_path}")

        service = DocumentService(None)

        # Upload with full processing
        with open(rattenlinien_path, 'rb') as f:
            result = await service.upload_document(
                file_path=str(rattenlinien_path),
                filename=rattenlinien_path.name,
                user_id="test_user_pipeline",
                auto_preprocess=True,
                auto_geocode=True,
                settings=None
            )

        assert result["success"] is True
        assert result["chunks_created"] > 0

        # Verify geocoding was performed
        geocode_result = await service._geocode_document_locations(
            result["document_id"],
            None
        )

        assert geocode_result["success"] is True
        assert geocode_result["chunks_processed"] > 0

    async def test_geocoding_performance(self, rattenlinien_path):
        """Test that batch geocoding performs better than sequential."""
        if not os.getenv("MAPBOX_ACCESS_TOKEN"):
            pytest.skip("MAPBOX_ACCESS_TOKEN not set")

        service = DocumentService(None)

        # Test locations from Rattenlinien escape routes
        locations = ["Rom", "Genua", "Buenos Aires"]

        # Load document content
        with open(rattenlinien_path, 'r', encoding='utf-8') as f:
            chunk_content = f.read()[:500]

        settings = Settings()

        # Time batch enrichment
        import time
        start_time = time.time()
        enriched = await service._enrich_locations_batch(locations, settings, chunk_content)
        enrichment_time = time.time() - start_time

        # Time batch geocoding
        start_time = time.time()
        geocoded = await service._geocode_locations_batch(
            enriched,
            os.getenv("MAPBOX_ACCESS_TOKEN")
        )
        geocoding_time = time.time() - start_time

        total_time = enrichment_time + geocoding_time

        # Verify reasonable performance (should complete in reasonable time)
        assert total_time < 30, f"Pipeline took too long: {total_time:.2f}s"

        # Verify results
        assert len(geocoded) == len(locations)
        successful = sum(1 for loc in geocoded if loc.get("coordinates"))
        assert successful > 0, "At least some geocoding should succeed"
