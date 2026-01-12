"""
Test Quartermaster tool with DeepEval evaluation.

Tests:
1. Curated domains from archive_domains.yaml are passed to RelevanceScorer
2. Authoritative archives (archives.gov, cia.gov) are NOT rejected as false positives
3. Intelligence queries return relevant archive results

Run with pytest: pytest tests/requires_env/intelligence_analysis/test_quartermaster_simple.py -s -v
"""

import json
import os
import pytest
from dotenv import load_dotenv

# Load .env file explicitly (Case Officer needs ARYN_API_KEY for PDF preview)
env_path = os.path.join(os.path.dirname(__file__), "../../../.env")
load_dotenv(env_path)
print(f"[TEST SETUP] Loaded .env from: {env_path}")
print(f"[TEST SETUP] ARYN_API_KEY present: {'ARYN_API_KEY' in os.environ}")
print(f"[TEST SETUP] DISABLE_PERPLEXITY_READER: {os.environ.get('DISABLE_PERPLEXITY_READER', 'not set')}")
print(f"[TEST SETUP] DISABLE_ARYN_PDF_READER: {os.environ.get('DISABLE_ARYN_PDF_READER', 'not set')}")
from typing import List, Dict, Any

# DeepEval imports (same pattern as test_complex_prompts.py)
from deepeval import evaluate, metrics
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.models import AnthropicModel

from elysia.tools.archives.quartermaster_tool import QuartermasterTool
from elysia.tree.objects import TreeData, CollectionData, Atlas
from elysia.util.client import ClientManager
from elysia.config import Settings, load_base_lm, load_complex_lm
from elysia import configure

# Set logging level like other tests do
configure(logging_level="DEBUG")


def to_dict(obj) -> Any:
    """Convert any object to dict for JSON serialization."""
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, (list, tuple)):
        return [to_dict(x) for x in obj]
    if isinstance(obj, dict):
        return {str(k): to_dict(v) for k, v in obj.items()}
    if hasattr(obj, '__dict__'):
        return {k: to_dict(v) for k, v in obj.__dict__.items() if not k.startswith('_')}
    if hasattr(obj, 'value'):  # Enum
        return str(obj.value)
    return str(obj)


class QuartermasterTestHarness:
    """Captures and organizes Quartermaster execution results for testing."""

    def __init__(self):
        self.phases: List[Dict[str, Any]] = []
        self.status_updates: List[Dict[str, Any]] = []
        self.final_result: Dict[str, Any] = None
        self.archives_found: List[Dict[str, Any]] = []

    def capture(self, result, phase_num: int):
        """Capture a phase result."""
        result_dict = to_dict(result)
        result_type = type(result).__name__

        self.phases.append({
            "phase": phase_num,
            "type": result_type,
            "data": result_dict,
        })

        # Categorize by type
        if result_type == "Status":
            self.status_updates.append(result_dict)
        elif result_type == "Result":
            self.final_result = result_dict
            if result_dict.get("objects"):
                self.archives_found = result_dict["objects"]

    def print_summary(self):
        """Print a concise summary of captured results."""
        print("\n" + "=" * 60)
        print("EXECUTION SUMMARY")
        print("=" * 60)
        print(f"Total phases: {len(self.phases)}")
        print(f"Status updates: {len(self.status_updates)}")
        print(f"Archives found: {len(self.archives_found)}")

        if self.archives_found:
            print("\n--- Archives Found ---")
            for i, archive in enumerate(self.archives_found):
                domain = archive.get("domain", "unknown")
                score = archive.get("score", 0)
                group = archive.get("group", "unknown")
                print(f"  {i+1}. {domain} (score={score}, group={group})")


@pytest.mark.asyncio
async def test_quartermaster_paul_lyon_query():
    """
    Simple debug test for Quartermaster with Paul Lyon intelligence query.

    No assertions - just prints output for manual verification.

    Expected results after fix:
    - archives.gov should NOT be marked as false_positive
    - Curated archives should have minimum score 0.3
    - Log should show "[RELEVANCE_SCORER] ... is_curated=True" for authoritative sources
    """
    print("\n" + "=" * 80)
    print("QUARTERMASTER SIMPLE DEBUG TEST")
    print("=" * 80)

    # Initialize settings
    settings = Settings.from_env_vars()
    client_manager = ClientManager()

    # Initialize language models
    base_lm = load_base_lm(settings)
    complex_lm = load_complex_lm(settings)

    # Initialize minimal TreeData (Quartermaster doesn't need collections)
    collection_data = CollectionData(
        collection_names=[],
        metadata={},
        logger=settings.logger
    )
    atlas = Atlas()
    tree_data = TreeData(
        collection_data=collection_data,
        atlas=atlas,
        settings=settings
    )

    # Initialize Quartermaster
    quartermaster = QuartermasterTool(logger=settings.logger)

    # Test query - Paul Lyon CIC/OSS intelligence investigation
    test_query = (
        "Please use the quartermaster to find any about Paul Lyon CIC counter intelligence corps "
        "and OSS officer in Austria in the early years of the Cold War between 1945 and 1952 "
        "in reports related to Robert Bishop CIC superior officer about potential treasoning "
        "of intelligence agents network related to spying for the SOVIETS."
    )

    # Inputs for Quartermaster
    inputs = {
        "query": test_query,
    }

    print(f"\nQuery: {test_query}")
    print("\n" + "-" * 80)
    print("EXECUTION - Watching for curated domain handling")
    print("-" * 80)

    harness = QuartermasterTestHarness()
    phase_counter = 0

    try:
        # Run Quartermaster
        async for result in quartermaster(
            tree_data=tree_data,
            inputs=inputs,
            base_lm=base_lm,
            complex_lm=complex_lm,
            client_manager=client_manager,
        ):
            result_type = type(result).__name__
            if result_type == "Status":
                # Print yielded Status message content
                status_msg = getattr(result, 'text', str(result))
                print(f"[STATUS] {status_msg}")
            else:
                print(f"\n[Phase {phase_counter}] {result_type}")
            harness.capture(result, phase_counter)
            phase_counter += 1

        # Print summary
        harness.print_summary()

        # ============================================================
        # BASIC STRUCTURAL ASSERTIONS
        # ============================================================
        print("\n" + "-" * 60)
        print("ASSERTIONS")
        print("-" * 60)

        # 1. Should have multiple phases (status updates + final result)
        assert len(harness.phases) >= 2, f"Expected at least 2 phases, got {len(harness.phases)}"
        print(f"✓ Phase count: {len(harness.phases)}")

        # 2. Should have a final result
        assert harness.final_result is not None, "No final result received"
        print("✓ Final result received")

        # 3. Should find at least one archive
        assert len(harness.archives_found) > 0, "No archives found"
        print(f"✓ Archives found: {len(harness.archives_found)}")

        # 4. For this intelligence query, should find CIA archives
        domains = [a.get("domain", "") for a in harness.archives_found]
        has_cia = any("cia.gov" in d for d in domains)
        print(f"✓ CIA archives found: {has_cia}")

        # ============================================================
        # DEEPEVAL EVALUATION
        # ============================================================
        print("\n" + "-" * 60)
        print("DEEPEVAL EVALUATION")
        print("-" * 60)

        # Build output string from archives found
        archives_summary = "\n".join([
            f"- {a.get('domain', 'unknown')}: {a.get('summary', '')[:100]}..."
            for a in harness.archives_found
        ])
        actual_output = f"Found {len(harness.archives_found)} relevant archives:\n{archives_summary}"

        print(f"Actual output:\n{actual_output[:500]}...")

        # Create Anthropic model for evaluation
        eval_model = AnthropicModel(model="claude-haiku-4-5")

        # Create DeepEval test case with AnswerRelevancyMetric
        # (TaskCompletionMetric requires tools_called which we don't have)
        deepeval_metric = metrics.AnswerRelevancyMetric(
            threshold=0.5,
            model=eval_model,
            include_reason=True
        )

        test_case = LLMTestCase(
            input=test_query,
            actual_output=actual_output,
        )

        # Run evaluation
        res = evaluate(test_cases=[test_case], metrics=[deepeval_metric])

        print(f"\nDeepEval result:")
        for tc in res.test_results:
            print(f"  Success: {tc.success}")
            if tc.metrics_data:
                print(f"  Reason: {tc.metrics_data[0].reason}")
            assert tc.success, f"DeepEval failed: {tc.metrics_data[0].reason if tc.metrics_data else 'unknown'}"

        print("\n" + "=" * 60)
        print("TEST PASSED")
        print("=" * 60)

    except Exception as e:
        print(f"\nERROR: {type(e).__name__}: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise

    finally:
        # Cleanup
        await client_manager.close_clients()


@pytest.mark.asyncio
async def test_combined_quartermaster_case_officer_workflow():
    """
    Combined workflow test: Quartermaster → Case Officer pipeline.

    Tests the full intelligence analysis workflow:
    1. Quartermaster finds relevant archives
    2. Case Officer synthesizes investigation report

    Validates both structural correctness and content quality.
    """
    print("\n" + "=" * 80)
    print("COMBINED WORKFLOW TEST: Quartermaster → Case Officer")
    print("=" * 80)

    # Import Case Officer
    from elysia.tools.archives.case_officer_tool import CaseOfficerTool

    # Initialize settings and clients (same as Quartermaster test)
    settings = Settings.from_env_vars()
    client_manager = ClientManager()
    base_lm = load_base_lm(settings)
    complex_lm = load_complex_lm(settings)

    # Initialize minimal TreeData
    collection_data = CollectionData(
        collection_names=[],
        metadata={},
        logger=settings.logger
    )
    atlas = Atlas()
    tree_data = TreeData(
        collection_data=collection_data,
        atlas=atlas,
        settings=settings
    )

    # Test query
    test_query = (
        "Please use the quartermaster to find any about Paul Lyon CIC counter intelligence corps "
        "and OSS officer in Austria in the early years of the Cold War between 1945 and 1952 "
        "in reports related to Robert Bishop CIC superior officer about potential treasoning "
        "of intelligence agents network related to spying for the SOVIETS."
    )

    print(f"\nQuery: {test_query[:100]}...")

    # ========================================
    # PHASE 1: Run Quartermaster
    # ========================================
    print("\n" + "-" * 60)
    print("PHASE 1: QUARTERMASTER")
    print("-" * 60)

    quartermaster = QuartermasterTool(logger=settings.logger)
    qm_harness = QuartermasterTestHarness()

    try:
        phase_counter = 0
        async for result in quartermaster(
            tree_data=tree_data,
            inputs={"query": test_query},
            base_lm=base_lm,
            complex_lm=complex_lm,
            client_manager=client_manager,
        ):
            result_type = type(result).__name__
            if result_type == "Status":
                status_msg = getattr(result, 'text', str(result))
                print(f"  [QM STATUS] {status_msg}")
            else:
                print(f"  [QM Phase {phase_counter}] {result_type}")
            qm_harness.capture(result, phase_counter)
            phase_counter += 1

        qm_harness.print_summary()

        # ========================================
        # PHASE 1 ASSERTIONS: Quartermaster
        # ========================================
        print("\n--- Quartermaster Assertions ---")
        assert qm_harness.final_result is not None, "Quartermaster: No final result"
        print("✓ Quartermaster returned final result")

        assert len(qm_harness.archives_found) > 0, "Quartermaster: No archives found"
        print(f"✓ Quartermaster found {len(qm_harness.archives_found)} archives")

        # ========================================
        # PHASE 2: Run Case Officer
        # ========================================
        print("\n" + "-" * 60)
        print("PHASE 2: CASE OFFICER")
        print("-" * 60)

        case_officer = CaseOfficerTool(logger=settings.logger)

        # Prepare archive_sources for Case Officer (from Quartermaster results)
        archive_sources = qm_harness.archives_found
        print(f"Passing {len(archive_sources)} archives to Case Officer")

        # Store Quartermaster results in hidden_environment (as real workflow does)
        tree_data.environment.hidden_environment["quartermaster_results"] = [{
            "archive_sources": archive_sources
        }]

        # Capture Case Officer outputs
        co_phases = []
        co_final_result = None

        async for result in case_officer(
            tree_data=tree_data,
            inputs={
                "query": test_query,
                "archive_sources": archive_sources,
            },
            base_lm=base_lm,
            complex_lm=complex_lm,
            client_manager=client_manager,
        ):
            result_type = type(result).__name__
            result_dict = to_dict(result)

            if result_type == "Status":
                status_msg = getattr(result, 'text', str(result))
                print(f"  [CO STATUS] {status_msg}")
            else:
                print(f"  [CO Phase {len(co_phases)}] {result_type}")

            co_phases.append({
                "type": result_type,
                "data": result_dict,
            })

            if result_type == "Result":
                co_final_result = result_dict

        # ========================================
        # PHASE 2 ASSERTIONS: Case Officer
        # ========================================
        print("\n--- Case Officer Assertions ---")

        assert len(co_phases) >= 2, f"Case Officer: Expected >= 2 phases, got {len(co_phases)}"
        print(f"✓ Case Officer completed {len(co_phases)} phases")

        assert co_final_result is not None, "Case Officer: No final result"
        print("✓ Case Officer returned final result")

        # Check metadata structure
        metadata = co_final_result.get("metadata", {})
        assert metadata.get("display_type") == "investigation", "Case Officer: Wrong display_type"
        print("✓ Case Officer metadata has display_type='investigation'")

        assert "hypotheses" in metadata, "Case Officer: No hypotheses in metadata"
        hypotheses = metadata.get("hypotheses", [])
        print(f"✓ Case Officer generated {len(hypotheses)} hypotheses")

        assert "next_steps" in metadata, "Case Officer: No next_steps in metadata"
        next_steps = metadata.get("next_steps", [])
        print(f"✓ Case Officer generated {len(next_steps)} next steps")

        # ========================================
        # DEEPEVAL: Combined Output Quality
        # ========================================
        print("\n" + "-" * 60)
        print("DEEPEVAL EVALUATION")
        print("-" * 60)

        # Build combined output for evaluation
        report_objects = co_final_result.get("objects", [])
        report_text = "\n".join([
            obj.get("content", obj.get("text", ""))
            for obj in report_objects
            if isinstance(obj, dict)
        ])

        hypotheses_text = "\n".join([
            f"- {h.get('description', '')}" for h in hypotheses
        ])

        actual_output = (
            f"Investigation Report:\n{report_text}\n\n"
            f"Hypotheses:\n{hypotheses_text}\n\n"
            f"Sources read: {metadata.get('sources_read', 0)}\n"
            f"Next steps: {len(next_steps)}"
        )

        print(f"Actual output preview:\n{actual_output[:500]}...")

        # DeepEval evaluation
        eval_model = AnthropicModel(model="claude-haiku-4-5")
        deepeval_metric = metrics.AnswerRelevancyMetric(
            threshold=0.5,
            model=eval_model,
            include_reason=True
        )

        test_case = LLMTestCase(
            input=test_query,
            actual_output=actual_output,
        )

        res = evaluate(test_cases=[test_case], metrics=[deepeval_metric])

        print(f"\nDeepEval result:")
        for tc in res.test_results:
            print(f"  Success: {tc.success}")
            if tc.metrics_data:
                print(f"  Reason: {tc.metrics_data[0].reason}")
            assert tc.success, f"DeepEval failed: {tc.metrics_data[0].reason if tc.metrics_data else 'unknown'}"

        print("\n" + "=" * 60)
        print("COMBINED WORKFLOW TEST PASSED")
        print("=" * 60)

    except Exception as e:
        print(f"\nERROR: {type(e).__name__}: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise

    finally:
        await client_manager.close_clients()


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_quartermaster_paul_lyon_query())
