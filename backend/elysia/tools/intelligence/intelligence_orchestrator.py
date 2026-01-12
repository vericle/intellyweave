# ABOUTME: Main intelligence analysis orchestration tool
# ABOUTME: Manages multi-agent intelligence analysis workflow

import asyncio
from typing import Any, AsyncGenerator, Dict, List

from elysia.objects import Error, Response, Status, Text, Tool, Update
from elysia.tree.objects import TreeData
from elysia.util.client import ClientManager

from .extractor_agent import ExtractorAgent
from .geospatial_agent import GeospatialAgent
from .mapper_agent import MapperAgent
from .network_agent import NetworkAgent
from .objects import (
    IntelligenceContext,
    IntelligenceMessage,
    IntelligenceResult,
    IntelligenceRole,
    IntelligenceState,
)
from .pattern_agent import PatternAgent

# from .suggestions import SuggestionsGenerator
from .synthesizer_agent import SynthesizerAgent

# from .temporal_agent import TemporalAgent


class IntelligenceOrchestrator(Tool):
    """
    Main tool for conducting intelligence analysis with multiple specialized agents.
    Coordinates sequential analysis to explore relationships and patterns.
    """

    def __init__(self, logger, **kwargs):
        """Initialize the intelligence orchestrator tool

        Args:
            logger: Logger instance for tracking analysis progress
            **kwargs: Additional arguments for tool initialization
        """
        self.logger = logger
        super().__init__(
            name="intelligence_orchestrator",
            description=(
                "Conducts comprehensive multi-agent intelligence analysis through a 4-phase sequential process. "
                "Phase 1: Entity extraction identifies persons, organizations, locations, dates, laws, and events. "
                "Phase 2: Relationship mapping establishes connections between extracted entities. "
                "Phase 3: Geospatial analysis maps entities and relationships focusing on geographic locations. "
                "Phase 4: Relational network patterns detection identifies key network structures and anomalies. "
                "Phase 5: Pattern detection uncovers recurring patterns and anomalies across all data. "
                "Phase 6: Final validation and synthesis that integrates all findings with follow-up questions suggestions. "
                "Provides actionable intelligence insights through coordinated agent collaboration."
            ),
            inputs={
                "initial_query": {
                    "description": "The original user query requiring intelligence analysis",
                    "type": "string",
                    "required": True,
                },
                "initial_response": {
                    "description": "The initial AI-generated response to be analyzed for deeper intelligence insights",
                    "type": "string",
                    "required": True,
                },
            },
            end=True,
            status="Initiating comprehensive intelligence analysis...",
            **kwargs,
        )

    async def __call__(
        self,
        tree_data: TreeData,
        inputs: Dict[str, Any],
        base_lm,
        complex_lm,
        client_manager: ClientManager,
        **kwargs,
    ) -> AsyncGenerator[
        IntelligenceMessage | IntelligenceResult | Status | Response | Error, None
    ]:
        """
        Execute the intelligence analysis workflow

        Args:
            tree_data: Tree data containing conversation context
            inputs: Tool inputs (initial_query, initial_response, initial_sources)
            base_lm: Base language model
            complex_lm: Complex language model
            client_manager: Client manager for database operations
            **kwargs: Additional arguments

        Yields:
            Analysis messages, updates, and final result
        """
        self.logger.info("Starting intelligence analysis")

        try:
            # Extract inputs
            initial_query = inputs.get("initial_query", "")
            initial_response = inputs.get("initial_response", "")

            # Validate inputs with detailed error messages
            if (
                not initial_query
                or not isinstance(initial_query, str)
                or initial_query.strip() == ""
            ):
                yield Error(
                    error_message="Invalid or missing initial_query",
                    feedback="The initial_query must be a non-empty string containing the user's intelligence analysis request.",
                )
                return

            if (
                not initial_response
                or not isinstance(initial_response, str)
                or initial_response.strip() == ""
            ):
                yield Error(
                    error_message="Invalid or missing initial_response",
                    feedback="The initial_response must be a non-empty string containing the AI-generated response to analyze.",
                )
                return

            # Read document results from environment (stored by query tools)
            initial_sources = []

            # DEBUG: Log environment structure
            if self.logger:
                self.logger.debug(
                    f"Environment keys: {list(tree_data.environment.environment.keys())}"
                )
                if "query" in tree_data.environment.environment:
                    self.logger.debug(
                        f"Query keys: {list(tree_data.environment.environment['query'].keys())}"
                    )

            # Get all query results from environment using the correct structure
            # Environment structure: environment[tool_name][result_name] = [{"metadata": {}, "objects": [...]}]
            if "query" in tree_data.environment.environment:
                query_data = tree_data.environment.environment["query"]

                # Iterate through all collection results under "query"
                for collection_name, result_list in query_data.items():
                    if self.logger:
                        self.logger.debug(
                            f"Processing collection: {collection_name}, result_list type: {type(result_list)}"
                        )

                    if isinstance(result_list, list):
                        for result_item in result_list:
                            if (
                                isinstance(result_item, dict)
                                and "objects" in result_item
                            ):
                                objects = result_item["objects"]
                                if self.logger:
                                    self.logger.debug(
                                        f"Found {len(objects)} objects in {collection_name}"
                                    )
                                initial_sources.extend(objects)
                            else:
                                if self.logger:
                                    self.logger.debug(
                                        f"Unexpected result_item structure: {type(result_item)}"
                                    )

            if self.logger:
                self.logger.debug(
                    f"Total sources loaded from environment: {len(initial_sources)}"
                )
                if initial_sources:
                    # Log sample entities from first source
                    sample = initial_sources[0]
                    self.logger.debug(
                        f"Sample source keys: {sample.keys() if isinstance(sample, dict) else 'not a dict'}"
                    )
                    if isinstance(sample, dict):
                        self.logger.debug(
                            f"Sample persons: {sample.get('persons', [])}"
                        )
                        self.logger.debug(
                            f"Sample organizations: {sample.get('organizations', [])}"
                        )

            # Initialize analysis context
            analysis_context = IntelligenceContext(
                initial_query=initial_query,
                initial_response=initial_response,
                initial_sources=initial_sources,
                analysis_history=[],
                current_phase="entity_extraction",
            )

            # Initialize agents with error handling
            try:
                extractor = ExtractorAgent(base_lm=complex_lm)
                mapper = MapperAgent(base_lm=base_lm)
                geospatial = GeospatialAgent(
                    base_lm=base_lm, client_manager=client_manager
                )
                network = NetworkAgent(base_lm=base_lm)
                pattern = PatternAgent(base_lm=base_lm)
                synthesizer = SynthesizerAgent(base_lm=base_lm)
            except Exception as e:
                self.logger.error(f"Failed to initialize intelligence agents: {e}")
                yield Error(
                    error_message="Agent initialization failed",
                    feedback=f"Could not initialize intelligence analysis agents: {str(e)}. This is likely a configuration issue.",
                )
                return

            yield Status("Intelligence analysis initiated. Agents are ready.")

            # Phase 1: Entity Extraction
            yield Status("Phase 1: Entity Extraction...")
            try:
                entity_msg = await extractor.extract(analysis_context)
                analysis_context.add_message(entity_msg)
                analysis_context.extracted_entities = entity_msg.findings
                yield entity_msg

                # Check success criteria: at least some entities should be found
                if not analysis_context.extracted_entities:
                    yield Status(
                        "Entity extraction found no entities. Analysis may be limited."
                    )

            except Exception as e:
                self.logger.error(f"Entity extraction failed: {e}")
                yield Error(
                    error_message="Entity extraction phase failed",
                    feedback=f"Failed to extract entities from the provided sources: {str(e)}. The analysis will continue with empty entity data.",
                )
                analysis_context.extracted_entities = []

            # Phase 2: Relationship Mapping
            yield Status("Phase 2: Relationship Mapping...")
            try:
                mapper_msg = await mapper.map(analysis_context)
                analysis_context.add_message(mapper_msg)
                analysis_context.relationship_map = (
                    mapper_msg.findings[0] if mapper_msg.findings else {}
                )
                yield mapper_msg
            except Exception as e:
                self.logger.error(f"Relationship mapping failed: {e}")
                yield Error(
                    error_message="Relationship mapping phase failed",
                    feedback=f"Failed to map relationships between entities: {str(e)}. The analysis will continue with empty relationship data.",
                )
                analysis_context.relationship_map = {}

            # Phase 3: Geospatial analysis maps entities and relationships focusing on geographic locations
            yield Status(
                "Phase 3: Geospatial analysis maps entities and relationships focusing on geographic locations..."
            )

            # Run geospatial analysis
            try:
                geospatial_msg = await geospatial.analyze(analysis_context)
                analysis_context.add_message(geospatial_msg)
                yield geospatial_msg
            except Exception as e:
                self.logger.error(f"Geospatial analysis failed: {e}")
                yield Error(
                    error_message="Geospatial analysis phase failed",
                    feedback=f"Failed to perform geospatial analysis: {str(e)}. Geographic visualization will not be available.",
                )

            yield Status(
                "Phase 4: Relational network patterns detection identifies key network structures and anomalies..."
            )
            # Run network analysis
            try:
                network_msg = await network.analyze(analysis_context)
                analysis_context.add_message(network_msg)
                yield network_msg
            except Exception as e:
                self.logger.error(f"Network analysis failed: {e}")
                yield Error(
                    error_message="Network analysis phase failed",
                    feedback=f"Failed to create network visualization: {str(e)}. Relationship network will not be available.",
                )

            yield Status(
                "Phase 5: Pattern detection uncovers recurring patterns and anomalies across all data...."
            )

            # Run pattern analysis
            try:
                pattern_msg = await pattern.analyze(analysis_context)
                analysis_context.add_message(pattern_msg)
                yield pattern_msg
            except Exception as e:
                self.logger.error(f"Pattern analysis failed: {e}")
                yield Error(
                    error_message="Pattern analysis phase failed",
                    feedback=f"Failed to detect patterns and anomalies: {str(e)}. Pattern insights will not be available.",
                )

            yield Status(
                "Phase 6: Final validation and synthesis that integrates all findings with follow-up questions suggestions..."
            )

            # Run synthesis
            try:
                synthesis_msg = await synthesizer.evaluate(analysis_context)
                analysis_context.add_message(synthesis_msg)
                yield synthesis_msg
            except Exception as e:
                self.logger.error(f"Synthesis failed: {e}")
                yield Error(
                    error_message="Synthesis phase failed",
                    feedback=f"Failed to synthesize intelligence findings: {str(e)}. Falling back to last successful response.",
                )

                # Fallback to last known good response from analysis context
                fallback_response = analysis_context.get_final_response()
                yield Response(fallback_response)

            # Generate final result
            final_response = analysis_context.get_final_response()

            # Create final result
            result = IntelligenceResult(
                final_response=final_response,
                analysis_context=analysis_context,
                total_phases=6,
            )

            yield result

            # Yield final text response
            yield Response(
                f"{final_response}\n\n[Intelligence Mode: Analysis completed across 4 phases]"
            )

            self.logger.info("Intelligence analysis completed")

        except Exception as e:
            self.logger.exception("Error during intelligence analysis")
            yield Error(
                error_message=f"Intelligence analysis failed: {str(e)}",
                feedback="An error occurred during the analysis process. Falling back to last successful response.",
            )
            # Fallback to last successful response from analysis context if available
            fallback_response = (
                analysis_context.get_final_response()
                if "analysis_context" in locals()
                else inputs.get("initial_response", "")
            )
            yield Response(fallback_response)

    def get_default_inputs(self) -> Dict[str, Any]:
        """Get default input values

        Returns:
            Dictionary of default inputs
        """
        return {
            "initial_query": "",
            "initial_response": "",
            "initial_sources": [],
        }
