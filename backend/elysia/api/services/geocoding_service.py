# ABOUTME: Service for geocoding locations using Mapbox API and LLM enrichment
import asyncio
import json
import os
import time
import urllib.parse
import warnings
from typing import Dict, List, Optional

import aiohttp

from elysia.api.core.log import logger
from elysia.config import Settings

# Suppress warnings
warnings.filterwarnings("ignore", message=".*sentencepiece.*", category=UserWarning)


class GeocodingService:
    """Service for geocoding locations using Mapbox API with LLM enrichment"""

    def __init__(self):
        """Initialize the geocoding service"""
        pass

    async def enrich_locations_batch(
        self,
        locations: List[str],
        settings: Settings,
        chunk_content: Optional[str] = None,
    ) -> List[Dict]:
        """
        Batch enrich multiple location names in a single LLM call for better performance.

        Args:
            locations: List of raw location names from entity extraction
            settings: Settings object for LLM configuration
            chunk_content: Optional chunk text content for additional context

        Returns:
            List of enriched location dictionaries with modern country context
        """
        start_time = time.time()

        if not locations:
            logger.debug("No locations to enrich (batch)")
            return []

        # Deduplicate locations while preserving order
        unique_locations = []
        seen = set()
        for loc in locations:
            if not loc or not isinstance(loc, str):
                continue

            loc_stripped = loc.strip()
            if not loc_stripped:
                continue

            if loc_stripped not in seen:
                unique_locations.append(loc_stripped)
                seen.add(loc_stripped)

        dropped = len(locations) - len(unique_locations)
        logger.debug(
            "Location batch normalised from %s raw values to %s unique (dropped=%s)",
            len(locations),
            len(unique_locations),
            dropped,
        )

        if not unique_locations:
            logger.debug("No valid unique locations after filtering (batch)")
            return []

        logger.info(
            f"[PERFORMANCE] Starting batch enrichment for {len(unique_locations)} unique locations"
        )

        # Create a temporary LM for location enrichment using Claude Haiku
        import dspy

        temp_lm = dspy.LM(
            model="anthropic/claude-haiku-4-5",
            max_tokens=12000,  # Increased for batch processing
            temperature=0.3,
            api_key=settings.API_KEYS.get("anthropic_api_key")
            or settings.API_KEYS.get("ANTHROPIC_API_KEY"),
        )

        # Build batch prompt for all locations
        locations_list = "\n".join(
            [f'{i + 1}. "{loc}"' for i, loc in enumerate(unique_locations)]
        )

        context_snippet = ""
        if chunk_content:
            context_snippet = chunk_content[:28000]
            logger.info(
                "Location enrichment context prepared (chars=%s)",
                len(context_snippet),
            )

        prompt = f"""Analyze these {len(unique_locations)} location names from a potentially historical document and provide enriched contextual information for geocoding.

{f'Context from document: "{context_snippet}..."' if context_snippet else ""}

Locations to enrich:
{locations_list}

Instructions:
- For EACH location, use the document context to disambiguate historical or ambiguous location names
- Prefer modern names that can be precisely geocoded (city, town, district, facility, courthouse, base, etc.).
- Resolve historical references to their present-day equivalents (e.g., "American occupation zone in Austria" -> "Salzburg, Austria")
- Do not invent new locations that are not implied by the text. Avoid outputs like entire countries, continents, or vague geopolitical regions
- Do NOT return Country-level locations. Only return specific places: Town, City, District, Places  or Region
- locationType must be EXACTLY ONE of these single words: Town, City, District, Region, Place
- CRITICAL: Order results by contextual importance - most important location FIRST, then descending by relevance to the document
- Always genrate response in English

Expected JSON structure:
[
  {{
    "locationName": "Modern geographical location name suitable for geocoding (e.g., "Berlin, Germany", "Wels, Austria")",
    "locationType": "MUST be exactly one of: Town, City, District, Region, Place",
    "description": "Concise description with historical context and time-frame. Include the current location info for disambiguation.",
    "country": "Modern country name where the location is found (e.g., "Germany", "Austria", Russia")"
  }},
  ...
]

If a location cannot be reasonably geocoded or is too ambiguous or is a Country, SKIP it entirely (do not include in the array).
Return ONLY deduplicated valid, geocodable locations as a JSON array, no explanations, no markdown."""

        try:
            llm_start = time.time()
            response = temp_lm(prompt)
            llm_duration = time.time() - llm_start
            logger.info(
                f"[PERFORMANCE] Batch LLM enrichment call completed in {llm_duration:.2f}s"
            )

            logger.info(f"Batch location enrichment response: {response}")
            # Normalize LLM response to raw text
            llm_output = (
                response[0] if isinstance(response, list) and response else response
            )

            if isinstance(llm_output, dict):
                for key in ("text", "content", "output", "result"):
                    candidate = llm_output.get(key)
                    if isinstance(candidate, str):
                        llm_output = candidate
                        break
                else:
                    llm_output = json.dumps(llm_output)

            json_text = str(llm_output).strip()

            # Strip markdown code block markers
            if json_text.startswith("```json"):
                json_text = json_text[7:]
            if json_text.startswith("```"):
                json_text = json_text[3:]
            if json_text.endswith("```"):
                json_text = json_text[:-3]
            json_text = json_text.strip()

            # Parse the batch response
            try:
                enriched_batch = json.loads(json_text)
            except json.JSONDecodeError as json_error:
                logger.error(
                    "Failed to parse LLM enrichment output (length=%s): %s",
                    len(json_text),
                    json_text[:500],
                )
                raise json_error

            # Process the batch results
            enriched_locations = []
            for i, (original_loc, enriched) in enumerate(
                zip(unique_locations, enriched_batch)
            ):
                if (
                    enriched
                    and isinstance(enriched, dict)
                    and "locationName" in enriched
                ):
                    # Validate and normalize locationType
                    location_type = enriched.get("locationType", "Place")
                    allowed_types = ["Town", "City", "Region", "District", "Place"]
                    
                    # Normalize to single word if needed
                    if "/" in location_type or "," in location_type:
                        # Take first word before delimiter
                        location_type = location_type.split("/")[0].split(",")[0].strip()
                    
                    # Filter out Country and only allow specific types
                    if location_type == "Country" or location_type not in allowed_types:
                        logger.debug(
                            f"Filtering out location '{original_loc}' with invalid type '{location_type}'"
                        )
                        continue
                    
                    enriched["locationType"] = location_type
                    enriched_locations.append(enriched)
                    logger.debug(
                        f"Batch enriched [{i + 1}/{len(unique_locations)}] '{original_loc}' -> '{enriched.get('locationName')}'"
                    )
                else:
                    # Fallback to original
                    logger.debug(
                        f"Batch enrichment missing data for location '{original_loc}', using fallback"
                    )
                    enriched_locations.append(
                        {
                            "locationName": original_loc,
                            "locationType": "Unknown",
                            "description": "",
                            "country": "",
                        }
                    )

            total_duration = time.time() - start_time
            logger.info(
                f"[PERFORMANCE] Batch enrichment completed in {total_duration:.2f}s ({len(enriched_locations)} locations, avg {total_duration / len(enriched_locations):.3f}s per location)"
            )


            logger.debug(f"Enriched locations: {json.dumps(enriched_locations)}")

            return enriched_locations

        except Exception as e:
            logger.error(
                f"Batch location enrichment failed: {e}, falling back to sequential"
            )
            raise e

    async def geocode_locations_batch(
        self, enriched_locations: List[Dict], mapbox_token: Optional[str] = None
    ) -> List[Dict]:
        """
        Batch geocode multiple locations using Mapbox Geocoding API v6.

        Args:
            enriched_locations: List of enriched location dicts with locationName, country, etc.
            mapbox_token: Optional Mapbox access token (defaults to env var)

        Returns:
            List of geocoded location dictionaries with coordinates
        """
        start_time = time.time()

        if not enriched_locations:
            logger.debug("No locations to geocode (batch)")
            return []

        # Get Mapbox token
        token = mapbox_token or os.getenv("MAPBOX_ACCESS_TOKEN")
        if not token:
            logger.error("MAPBOX_ACCESS_TOKEN not set, cannot perform batch geocoding")
            return []

        logger.info(
            f"[PERFORMANCE] Starting batch geocoding for {len(enriched_locations)} locations"
        )

        # Build batch request payload
        batch_queries = []
        for loc in enriched_locations:
            location_name = loc.get("locationName", "")
            if not location_name:
                batch_queries.append(None)  # Placeholder for skipped locations
                continue

            query = {
                "q": location_name,
                "types": "locality,place,district,region",
                "limit": 1,
                "permanent": True,  # Allow caching of results
                "autocomplete": False,  # Exact matches for historical documents
                "language": "en",
            }

            batch_queries.append(query)

        # Filter out None placeholders
        valid_queries = [q for q in batch_queries if q is not None]
        skipped = len(batch_queries) - len(valid_queries)
        if skipped:
            logger.debug(
                "Skipped %s locations with empty names before geocoding", skipped
            )
        if not valid_queries:
            logger.warning("No valid queries for batch geocoding")
            return []

        try:
            # Single batch API call to Mapbox v6
            api_start = time.time()
            async with aiohttp.ClientSession() as session:
                url = "https://api.mapbox.com/search/geocode/v6/batch"
                params = {"access_token": token, "permanent": "true"}

                logger.debug(
                    f"Batch geocoding request: {len(valid_queries)} queries to {url}"
                )

                async with session.post(
                    url,
                    params=params,
                    json=valid_queries,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(
                            f"Mapbox batch API returned status {response.status}: {error_text}"
                        )
                        return []

                    data = await response.json()
                    api_duration = time.time() - api_start
                    logger.info(
                        f"[PERFORMANCE] Batch geocoding API call completed in {api_duration:.2f}s"
                    )

            # Process batch results
            batch_results = data.get("batch", [])
            geocoded_locations = []

            for i, (loc, result) in enumerate(zip(enriched_locations, batch_results)):
                location_name = loc.get("locationName", "")

                if not result.get("features"):
                    logger.debug(f"No geocoding result for '{location_name}'")
                    geocoded_locations.append(
                        {
                            **loc,
                            "coordinates": None,
                            "locationName": None,
                            "geocoded_relevance": None,
                        }
                    )
                    continue

                feature = result["features"][0]
                coordinates = feature.get("geometry", {}).get("coordinates")

                if not coordinates or len(coordinates) < 2:
                    logger.debug(f"Invalid coordinates for '{location_name}'")
                    geocoded_locations.append(
                        {
                            **loc,
                            "coordinates": None,
                            "latitude": None,
                            "longitude": None,
                            "name": location_name,  # Changed to match frontend expectation
                            "locationType": loc.get("locationType", "Location"),
                        }
                    )
                    continue

                longitude, latitude = coordinates[0], coordinates[1]
                place_name = feature["properties"].get("full_address") or feature[
                    "properties"
                ].get("name")
                place_formatted = feature["properties"].get("place_formatted")

                # Use context from v6 API
                context = feature["properties"].get("context", {})

                geocoded_locations.append(
                    {
                        **loc,
                        "coordinates": [longitude, latitude],
                        "latitude": latitude,
                        "longitude": longitude,
                        "name": loc.get("locationName") or place_name,
                        "locationType": loc.get("locationType", "Location"),
                    }
                )

                logger.debug(
                    f"Batch geocoded [{i + 1}/{len(enriched_locations)}] '{location_name}' -> {place_name} ({latitude:.4f}, {longitude:.4f})"
                )

            total_duration = time.time() - start_time
            success_count = sum(
                1 for loc in geocoded_locations if loc.get("coordinates")
            )
            logger.info(
                f"[PERFORMANCE] Batch geocoding completed in {total_duration:.2f}s ({success_count}/{len(enriched_locations)} successful, avg {total_duration / len(enriched_locations):.3f}s per location)"
            )

            return geocoded_locations

        except aiohttp.ClientError as e:
            logger.error(f"Mapbox batch API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Batch geocoding error: {e}")
            return []

    async def geocode_location(self, location_name: str) -> Optional[Dict]:
        """
        Geocode a location name using Mapbox Geocoding API v6 forward geocoding

        Args:
            location_name: Name of location to geocode

        Returns:
            Dictionary with lat/lon and place metadata or None if geocoding fails
        """
        try:
            # Validate input
            if not location_name or not isinstance(location_name, str):
                return None

            location_text = location_name.strip()
            if not location_text:
                return None

            # Mapbox configuration
            MAPBOX_ACCESS_TOKEN = os.getenv("MAPBOX_ACCESS_TOKEN")
            if not MAPBOX_ACCESS_TOKEN:
                logger.error("MAPBOX_ACCESS_TOKEN environment variable not set")
                return None

            # Use v6 forward geocoding endpoint
            MAPBOX_BASE_URL = "https://api.mapbox.com/search/geocode/v6/forward"
            url = MAPBOX_BASE_URL

            params = {
                "access_token": MAPBOX_ACCESS_TOKEN,
                "q": location_text,  # v6 uses query parameter instead of path
                "limit": 1,
                "types": "locality,place,district,region",
                "permanent": "true",  # Enable permanent geocoding for storage
                "autocomplete": "false",  # Exact matches only
                "language": "en",
            }

            logger.debug(
                "Geocoding single location '%s' via %s with params=%s",
                location_text,
                url,
                {"limit": params["limit"], "types": params["types"]},
            )

            # Use aiohttp for async requests
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, params=params, timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status != 200:
                        logger.warning(
                            f"Mapbox API returned status {response.status} for '{location_text}'"
                        )
                        return None

                    data = await response.json()

                    if not data.get("features") or len(data["features"]) == 0:
                        logger.warning(f"No geocoding results for '{location_text}'")
                        return None

                    feature = data["features"][0]

                    # Extract coordinates (Mapbox returns [longitude, latitude])
                    coordinates = feature.get("geometry", {}).get("coordinates")
                    if not coordinates or len(coordinates) < 2:
                        logger.warning(
                            f"No valid coordinates in response for '{location_text}'"
                        )
                        return None

                    longitude, latitude = coordinates[0], coordinates[1]

                    # Extract metadata from v6 response
                    properties = feature.get("properties", {})
                    place_name = properties.get("full_address") or properties.get("name") or location_text
                    relevance = properties.get("match_code", {}).get("confidence", 0)
                    feature_type = properties.get("feature_type", "")

                    # Map v6 feature types to readable types
                    type_mapping = {
                        "country": "Country",
                        "region": "Region",
                        "place": "City",
                        "locality": "Town",
                        "district": "District",
                    }
                    location_type = type_mapping.get(feature_type, feature_type.title() if feature_type else "Unknown")

                    logger.info(
                        f"Geocoded '{location_text}' -> {place_name} ({latitude}, {longitude}) [type: {location_type}, confidence: {relevance}]"
                    )

                    return {
                        "lat": latitude,
                        "lon": longitude,
                        "place_name": place_name,
                        "location_type": location_type,
                        "relevance": relevance,
                    }

        except aiohttp.ClientError as e:
            logger.error(f"Mapbox API error for '{location_name}': {e}")
            return None
        except Exception as e:
            logger.error(f"Geocoding error for '{location_name}': {e}")
            return None