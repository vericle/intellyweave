"""
Integration test for intelligence orchestrator.

This test validates the intelligence orchestrator workflow by:
1. Running a query through the intelligence orchestrator with real database data
2. Testing that orchestrator reads from tree_data.environment (not direct inputs)
3. Printing results from each phase (entity extraction, mapping, geospatial, network, pattern, synthesis)

Requires:
- ANTHROPIC_API_KEY or other LLM provider API key
- Weaviate instance with ELYSIA_CHUNKED_elysia_uploaded_documents__ collection
"""

import pytest
import json
from elysia.tools.intelligence import IntelligenceOrchestrator
from elysia.util.client import ClientManager
from elysia.tree.objects import TreeData, CollectionData, Atlas
from elysia.config import Settings, load_base_lm, load_complex_lm


@pytest.mark.asyncio
async def test_intelligence_orchestrator():
    """
    Integration test for intelligence orchestrator.
    Runs a real query through the intelligence orchestrator with real database data.
    Orchestrator reads from environment (not direct inputs) - tests proper integration.
    Prints results from each phase for debugging payload structure.
    """
    print("\n" + "=" * 80)
    print("INTELLIGENCE ORCHESTRATOR INTEGRATION TEST")
    print("=" * 80)
    
    # Initialize settings from environment variables
    settings = Settings.from_env_vars()
    client_manager = ClientManager()
    
    # Initialize language models
    base_lm = load_base_lm(settings)
    complex_lm = load_complex_lm(settings)
    
    # Collection name to use for the test
    collection_name = "ELYSIA_CHUNKED_elysia_uploaded_documents__"
    
    # Initialize CollectionData with real metadata
    collection_data = CollectionData(
        collection_names=[collection_name],
        metadata={},
        logger=settings.logger
    )
    
    # Load collection metadata from Weaviate
    await collection_data.set_collection_names([collection_name], client_manager)
    
    # Initialize Atlas with default values
    atlas = Atlas()
    
    # Initialize TreeData with real collection data
    tree_data = TreeData(
        collection_data=collection_data,
        atlas=atlas,
        settings=settings
    )
    
    # Initialize orchestrator
    orchestrator = IntelligenceOrchestrator(logger=settings.logger)
    
    # Test query - analyzing Nazi escape routes (Rattenlinien)
    test_query = "Analyze the Rattenlinien Nazi escape routes, identifying key persons involved (war criminals, church figures), organizations (CIC, Vatican, SS), and locations (Rome, Argentina, Flensburg)"

    # Initial response simulating what would come from the tree's first response
    initial_response = "The database contains information about Rattenlinien (Nazi Rat Lines), the escape routes used by Nazi war criminals after WWII to flee to South America via Italy and Spain, with involvement from the Vatican and US intelligence."
    
    # CRITICAL TDD SETUP: Populate environment with mock query results
    # This simulates what the query tool would have stored in environment
    # Using data from Rattenlinien (Nazi Rat Lines) escape routes document
    mock_query_results = [
        {
            "content": "Krunoslav Draganović organisierte zusammen mit Bischof Alois Hudal die Fluchtrouten. Er war für das Counter Intelligence Corps (CIC) der USA tätig.",
            "uuid": "test-uuid-1",
            "collection_name": collection_name,
            "chunk_spans": [18071, 20022],
            "persons": ["Krunoslav Draganović", "Alois Hudal"],
            "organizations": ["CIC", "Ustascha", "Vatikan"],
            "locations": ["Rom", "Genua"],
            "title": "Rattenlinien_cleaned.txt",
            "_REF_ID": "query_test_0_0"
        },
        {
            "content": "Adolf Eichmann und Josef Mengele flohen über die Rattenlinien nach Argentinien. Juan Perón empfing die Kriegsverbrecher mit offenen Armen.",
            "uuid": "test-uuid-2",
            "collection_name": collection_name,
            "chunk_spans": [30068, 31966],
            "persons": ["Adolf Eichmann", "Josef Mengele", "Juan Perón"],
            "organizations": ["SS", "NS-Regime"],
            "locations": ["Buenos Aires", "Argentinien", "Rom", "Südtirol"],
            "geocoded_location": "Buenos Aires",
            "latitude": -34.6037,
            "longitude": -58.3816,
            "title": "Rattenlinien_cleaned.txt",
            "_REF_ID": "query_test_0_1"
        },
        {
            "content": "Die Rattenlinie Nord führte nach Schleswig-Holstein in Richtung Flensburg, wo im Mai 1945 der Sonderbereich Mürwik mit der letzten Reichsregierung entstand.",
            "uuid": "test-uuid-3",
            "collection_name": collection_name,
            "chunk_spans": [6583, 8646],
            "persons": ["Klaus Barbie", "Franz Stangl", "Erich Priebke", "Walter Rauff"],
            "organizations": ["SS", "Gestapo", "Stille Hilfe"],
            "locations": ["Flensburg", "Schleswig-Holstein", "Barcelona", "Spanien"],
            "geocoded_location": "Flensburg",
            "latitude": 54.7937,
            "longitude": 9.4469,
            "title": "Rattenlinien_cleaned.txt",
            "_REF_ID": "query_test_0_2"
        }
    ]

    # Add mock results to environment using the correct structure
    # Environment structure: environment[tool_name][result_name] = [{"metadata": {}, "objects": [...]}]
    tree_data.environment.add_objects(
        tool_name="query",
        name=collection_name,
        objects=mock_query_results,
        metadata={
            "collection_name": collection_name,
            "query_type": "hybrid",
            "query_text": "Rattenlinien Nazi escape routes war criminals Vatican CIC"
        }
    )

    # Test inputs - orchestrator should read from environment, not take initial_sources
    inputs = {
        "initial_query": test_query,
        "initial_response": initial_response,
        # Removed initial_sources - orchestrator must read from tree_data.environment
    }

    print(f"\nTest Query: {test_query}")
    print(f"Initial Response: {initial_response}")
    print(f"Collection: {collection_name}")

    # Verify environment was populated correctly
    env_check = tree_data.environment.find('query', collection_name)
    if env_check:
        total_docs = sum(len(item.get('objects', [])) for item in env_check)
        print(f"Environment Sources: {total_docs} documents (POPULATED FOR TDD)")
        print(f"Sample entities from Rattenlinien: persons={mock_query_results[0]['persons']}, orgs={mock_query_results[0]['organizations']}")
    else:
        print(f"Environment Sources: 0 documents (NOT POPULATED - TEST WILL FAIL)")

    print("\n" + "-" * 80)
    print("EXECUTION PHASES - Testing Environment Integration")
    print("-" * 80)
    
    phase_counter = 0
    
    def serialize_to_json(obj):
        """Convert object to JSON-serializable format"""
        # Handle None
        if obj is None:
            return None
        
        # Handle basic types
        if isinstance(obj, (str, int, float, bool)):
            return obj
        
        # Handle lists and tuples
        if isinstance(obj, (list, tuple)):
            return [serialize_to_json(item) for item in obj]
        
        # Handle dictionaries
        if isinstance(obj, dict):
            return {str(k): serialize_to_json(v) for k, v in obj.items()}
        
        # Handle enums
        if hasattr(obj, 'value'):
            return str(obj.value)
        
        # Handle objects with __dict__
        if hasattr(obj, '__dict__'):
            result = {'__type__': type(obj).__name__}
            for key, value in obj.__dict__.items():
                if not key.startswith('_'):  # Skip private attributes
                    try:
                        result[key] = serialize_to_json(value)
                    except Exception as e:
                        result[key] = f"<serialization error: {e}>"
            return result
        
        # Fallback to string representation
        return str(obj)
    
    try:
        # Run the orchestrator
        async for result in orchestrator(
            tree_data=tree_data,
            inputs=inputs,
            base_lm=base_lm,
            complex_lm=complex_lm,
            client_manager=client_manager,
        ):
            result_type = type(result).__name__
            
            print(f"\n{'='*80}")
            print(f"[Phase {phase_counter}] Result Type: {result_type}")
            print('='*80)
            
            # Serialize the complete object to JSON
            try:
                serialized = serialize_to_json(result)
                print(json.dumps(serialized, indent=2, ensure_ascii=False))
            except Exception as e:
                print(f"ERROR: Could not serialize object: {e}")
                print(f"Object __dict__: {result.__dict__ if hasattr(result, '__dict__') else 'No __dict__'}")
            
            print("-" * 80)
            
            phase_counter += 1
        
        print(f"\n✓ Intelligence orchestrator completed")
        print(f"✓ Total phases executed: {phase_counter}")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ Error during intelligence orchestrator execution:")
        print(f"  Error Type: {type(e).__name__}")
        print(f"  Error Message: {str(e)}")
        import traceback
        print(f"\nTraceback:")
        print(traceback.format_exc())
        print("=" * 80)
        raise
    
    finally:
        # Cleanup
        await client_manager.close_clients()
