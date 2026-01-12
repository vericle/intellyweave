# ABOUTME: Geospatial Agent for intelligence analysis
# ABOUTME: Analyzes geospatial patterns and returns text-based geographic findings

from typing import Any, Dict, List

import dspy

from elysia.api.core.log import logger

from .objects import IntelligenceContext, IntelligenceMessage, IntelligenceRole


class GeospatialAnalysisSignature(dspy.Signature):
    """Analyze geospatial patterns in intelligence operations and identify key locations.

    Extract location entities and their significance to the intelligence analysis.
    Create structured text findings explaining geographic patterns, operational locations,
    and spatial relationships between entities.

    Return longitude, latitude, heatmap weights, and route (if any) for each location.
    Assign intelligence activity weight (1-10 scale) for heatmap visualization.
    Generate routes connecting key locations if applicable and relevant.
    """

    sources: List[Dict[str, Any]] = dspy.InputField(
        desc="Source documents containing location references, addresses, and geographic context for intelligence analysis"
    )
    extracted_entities: List[Dict[str, Any]] = dspy.InputField(
        desc="All extracted entities from the intelligence analysis, including any location-related entities"
    )
    relationships: Dict[str, Any] = dspy.InputField(
        desc="Relationship mappings between entities showing connections, associations, and interactions"
    )
    query_context: str = dspy.InputField(
        desc="The original intelligence query to focus geospatial analysis on relevant locations"
    )

    geographic_findings: List[Dict[str, Any]] = dspy.OutputField(
        desc="""List of geographic intelligence findings as structured text objects. Each finding must have:
        - name: Location or geographic pattern name (e.g., 'Vienna Operations Center', 'Soviet Border Surveillance')
        - type: Category (e.g., 'Operational Location', 'Intelligence Activity', 'Geographic Pattern')
        - description: What the location/pattern represents
        - assessment: Why it's significant to the intelligence analysis
        - confidence: Confidence score 0.0-1.0
        - reasoning: Evidence supporting this finding
        - latitude: Numeric latitude coordinate (-90 to 90)
        - longitude: Numeric longitude coordinate (-180 to 180)
        - route: Array of [longitude, latitude] coordinate pairs defining start and end points of route path as list[list[float]] (first item must be same coordinates as the location).
        - weight: Intelligence activity intensity (1-10 scale) where 10=highest activity (this is used for heatmap visualization)
            Assign based on operational importance: primary hubs=9-10, secondary sites=6-8, 
            minor locations=3-5, peripheral sites=1-2. Used for heatmap visualization.

        If you cannot determine the endpoint location latitude and longitude return empty array [] for route.

        Focus on geographic intelligence - locations, patterns, and spatial relationships."""
    )


class GeospatialAgent:
    """Agent responsible for geospatial intelligence analysis - returns text-based geographic findings"""

    def __init__(self, base_lm, client_manager=None):
        self.lm = base_lm
        self.client_manager = client_manager
        self.chain = dspy.ChainOfThought(GeospatialAnalysisSignature)

    async def analyze(self, context: IntelligenceContext) -> IntelligenceMessage:
        """Analyze geospatial aspects and return text-based geographic intelligence findings"""
        try:
            logger.debug(
                f"Starting geospatial analysis for query: {context.initial_query}"
            )
            logger.debug(f"Input sources count: {len(context.initial_sources)}")
            logger.debug(f"Extracted entities count: {len(context.extracted_entities)}")

            # Run DSPy chain to identify geographic intelligence findings
            with dspy.settings.context(lm=self.lm):
                result = self.chain(
                    sources=context.initial_sources,
                    relationships=context.relationship_map,
                    extracted_entities=context.extracted_entities,
                    query_context=context.initial_query,
                )

            logger.debug(
                f"DSPy chain generated {len(result.geographic_findings)} geographic findings"
            )

            # Structure findings from DSPy output
            findings = []
            for finding_data in result.geographic_findings:
                # Extract fields from DSPy output for structured location data

                route: list[list[float]] = []
                try:
                    route =  list(finding_data.get("route", []))
                except Exception:
                    logger.debug("No valid route data found, setting empty route")
                    route = [] 

                finding = {
                    "name": str(finding_data.get("name", "Unknown Location")),
                    "type": str(finding_data.get("type", "Geographic Finding")),
                    "description": str(finding_data.get("description", "")),
                    "assessment": str(finding_data.get("assessment", "")),
                    "confidence": float(finding_data.get("confidence", 0.75)),
                    "reasoning": str(finding_data.get("reasoning", "")),
                    "latitude": float(finding_data.get("latitude", 0.0)),
                    "longitude": float(finding_data.get("longitude", 0.0)),
                    "route": route,
                    "weight": int(
                        finding_data.get("weight",0)
                    ), 
                }
                findings.append(finding)


            logger.debug(f"Structured {len(findings)} geographic findings")

            # If no findings, create a placeholder
            if not findings:
                findings = [
                    {
                        "name": "No Geographic Intelligence",
                        "type": "Analysis Result",
                        "description": "No specific geographic locations or patterns identified in available sources",
                        "assessment": "Insufficient geographic data to generate location-based intelligence findings",
                        "confidence": 0.9,
                        "reasoning": "Analysis completed but no location entities found in source documents",
                        "latitude": None,
                        "longitude": None,
                        "route": [],
                        "weight": None,
                    }
                ]

            location_count = len(
                [
                    f
                    for f in findings
                    if f.get("type") in ["Operational Location", "Location"]
                ]
            )

            # Build message findings with route data
            message_findings = findings.copy()

            # Add route data as metadata if available
            message_metadata = {}
           

            message = IntelligenceMessage(
                agent_role=IntelligenceRole.GEOSPATIAL,
                content=f"Geospatial analysis identified {len(findings)} geographic intelligence findings",
                findings=message_findings,
                reasoning=result.reasoning,
                analysis_phase="geospatial_analysis",
                confidence_score=result.confidence if hasattr(result, "confidence") else 0.0,
            )

            logger.debug(f"Returning geospatial analysis message: {message.content}")

            return message

        except Exception as e:
            logger.error(f"Error in geospatial analysis: {str(e)}")
            # Return error message as IntelligenceMessage with error finding
            return IntelligenceMessage(
                agent_role=IntelligenceRole.GEOSPATIAL,
                content=f"Geospatial analysis encountered an error but completed",
                findings=[
                    {
                        "name": "Analysis Error",
                        "type": "System Message",
                        "description": f"Geospatial processing error: {str(e)}",
                        "assessment": "Unable to complete full geographic analysis due to processing error",
                        "confidence": 0.9,
                        "reasoning": f"Exception during geospatial analysis: {type(e).__name__}",
                        "latitude": None,
                        "longitude": None,
                        "route": [],
                        "weight": None,
                    }
                ],
                reasoning=f"Error during geospatial processing: {str(e)}",
                analysis_phase="geospatial_analysis",
                confidence_score=0.9,
            )