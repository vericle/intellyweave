"""
Test more complex prompts that require multiple logical steps.
E.g. aggregation _and_ query.
Focusing only on whether the correct tools are called, not the accuracy of the results.
"""

import pytest
from copy import deepcopy
from deepeval import evaluate, metrics
from weaviate.classes.config import Configure
from deepeval.test_case import LLMTestCase, LLMTestCaseParams, ToolCall

from elysia import Tree, Settings
from elysia.util.client import ClientManager
from elysia import configure, preprocess
from elysia.preprocessing.collection import preprocessed_collection_exists

configure(logging_level="DEBUG")


def get_tools_called(tree: Tree, user_prompt: str):
    tools_called = []
    if user_prompt in tree.actions_called:
        for action in tree.actions_called[user_prompt]:
            if action["name"] in tree.tools:
                tools_called.append(
                    ToolCall(
                        name=action["name"],
                        description=tree.tools[action["name"]].description,
                        input_parameters=action["inputs"],
                        output=action["output"] if "output" in action else [],
                    )
                )
    return tools_called


async def run_tree(user_prompt: str, collection_names: list[str]) -> Tree:

    tree = Tree()

    async for result in tree.async_run(
        user_prompt,
        collection_names=collection_names,
    ):
        pass
    return tree


@pytest.mark.asyncio
async def test_aggregation_and_query():
    """
    Test that the correct tools are called for a prompt that requires both aggregation and query.
    """

    # if the collection is not found, load the weather data
    client_manager = ClientManager()
    if not client_manager.client.collections.exists("Weather"):
        import weaviate.classes.config as wvc
        from datasets import load_dataset
        
        with client_manager.connect_to_client() as client:
            client.collections.create(
                "Weather",
                description="Daily weather information including temperature, wind speed, precipitation, pressure etc.",
                vector_config=Configure.Vectors.self_provided(),  # Changed from Configure.Vectorizer.none()
                properties=[
                    wvc.Property(name="date", data_type=wvc.DataType.DATE),
                    wvc.Property(name="humidity", data_type=wvc.DataType.NUMBER),
                    wvc.Property(name="precipitation", data_type=wvc.DataType.NUMBER),
                    wvc.Property(name="wind_speed", data_type=wvc.DataType.NUMBER),
                    wvc.Property(name="visibility", data_type=wvc.DataType.NUMBER),
                    wvc.Property(name="pressure", data_type=wvc.DataType.NUMBER),
                    wvc.Property(name="temperature", data_type=wvc.DataType.NUMBER, description="temperature value in Celsius")
                ]
            )
            
            weather_dataset = load_dataset("weaviate/agents", "query-agent-weather", split="train", streaming=True)
            weather_collection = client.collections.get("Weather")
            
            with weather_collection.batch.dynamic() as batch:
                for item in weather_dataset:
                    batch.add_object(properties=item["properties"])
    
    # Preprocess Weather collection to enable query/aggregate tools
    from elysia import preprocess
    preprocess("Weather")

    user_prompt = "What was the maximum weather last year?"
    tree = await run_tree(user_prompt, ["Weather"])

    print(f"Tree decision history: {tree.decision_history}")

    all_decision_history = []
    for iteration in tree.decision_history:
        all_decision_history.extend(iteration)

    # assert "aggregate" in all_decision_history
    # assert "query" in all_decision_history

    # -- DeepEval tests --
    deepeval_metric = metrics.TaskCompletionMetric(
        threshold=0.5, model="gpt-4o-mini", include_reason=True
    )

    tools_called = get_tools_called(tree, user_prompt)

    print(f"Tools called: {tools_called}")

    test_case = LLMTestCase(
        input=user_prompt,
        actual_output=tree.tree_data.conversation_history[-1]["content"],
        tools_called=tools_called,
    )

    print(f"Test case: {test_case}")

    res = evaluate(test_cases=[test_case], metrics=[deepeval_metric])

    print(f"Evaluation result: {res}")

    for test_case in res.test_results:
        assert test_case.success, test_case.metrics_data[0].reason


@pytest.mark.asyncio
async def test_query_with_chunking():
    """
    Test that the correct tools are called for a prompt that requires both aggregation and query.
    """

    try:
        # if the collection is not found, skip the test
        client_manager = ClientManager()
        if not client_manager.client.collections.exists(
            "Weaviate_documentation"
        ) or not client_manager.client.collections.exists("Weaviate_blogs"):
            pytest.skip("Collections not found in Weaviate")

        if not preprocessed_collection_exists("Weaviate_documentation", client_manager):
            preprocess(
                "Weaviate_documentation",
                client_manager,
            )
        if not preprocessed_collection_exists("Weaviate_blogs", client_manager):
            preprocess(
                "Weaviate_blogs",
                client_manager,
            )

        user_prompt = "What is Weaviate"
        tree = await run_tree(user_prompt, ["Weaviate_documentation", "Weaviate_blogs"])

        print(f"Tree decision history: {tree.decision_history}")

        all_decision_history = []
        for iteration in tree.decision_history:
            all_decision_history.extend(iteration)

        assert "query" in all_decision_history
        env_key = (
            "summarise_items"
            if "summarise_items" in tree.tree_data.environment.environment
            else "query"
        )
        assert env_key in tree.tree_data.environment.environment

        print(f"Environment key: {env_key}")

        collections_queried = list(
            tree.tree_data.environment.environment[env_key].keys()
        )

        print(f"Collections queried: {collections_queried}")

        # for collection in collections_queried:
        #     assert collection in tree.tree_data.environment.environment[env_key]
        #     assert len(tree.tree_data.environment.environment[env_key][collection]) > 0
        #     for item in tree.tree_data.environment.environment[env_key][collection][0][
        #         "objects"
        #     ]:
        #         assert "chunk_spans" in item and item["chunk_spans"] is not []

        # -- DeepEval tests --
        deepeval_metric = metrics.TaskCompletionMetric(
            threshold=0.5, model="gpt-4o-mini", include_reason=True
        )

        tools_called = get_tools_called(tree, user_prompt)

        print(f"Tools called: {tools_called}")

        test_case = LLMTestCase(
            input=user_prompt,
            actual_output=tree.tree_data.conversation_history[-1]["content"],
            tools_called=tools_called,
        )

        print(f"Test case: {test_case}")

        res = evaluate(test_cases=[test_case], metrics=[deepeval_metric])

        print(f"Evaluation result: {res}")

        for test_case in res.test_results:
            assert test_case.success, test_case.metrics_data[0].reason
    finally:
        # remove the chunked collection so future tests will always chunk
        client_manager = ClientManager()
        with client_manager.connect_to_client() as client:
            if client.collections.exists("ELYSIA_CHUNKED_weaviate_documentation__"):
                client.collections.delete("ELYSIA_CHUNKED_weaviate_documentation__")
            if client.collections.exists("ELYSIA_CHUNKED_weaviate_blogs__"):
                client.collections.delete("ELYSIA_CHUNKED_weaviate_blogs__")


@pytest.mark.asyncio
async def test_impossible_query():
    """
    Test that when given a task that is not possible, the model does not attempt it (too many times).
    """

    # if the collection is not found, load the weather data
    client_manager = ClientManager()
    if not client_manager.client.collections.exists("Weather"):
        import weaviate.classes.config as wvc
        from datasets import load_dataset
        
        with client_manager.connect_to_client() as client:
            client.collections.create(
                "Weather",
                description="Daily weather information including temperature, wind speed, precipitation, pressure etc.",
                vector_config=wvc.Configure.Vectorizer.self_provided(),
                properties=[
                    wvc.Property(name="date", data_type=wvc.DataType.DATE),
                    wvc.Property(name="humidity", data_type=wvc.DataType.NUMBER),
                    wvc.Property(name="precipitation", data_type=wvc.DataType.NUMBER),
                    wvc.Property(name="wind_speed", data_type=wvc.DataType.NUMBER),
                    wvc.Property(name="visibility", data_type=wvc.DataType.NUMBER),
                    wvc.Property(name="pressure", data_type=wvc.DataType.NUMBER),
                    wvc.Property(name="temperature", data_type=wvc.DataType.NUMBER, description="temperature value in Celsius")
                ]
            )
            
            weather_dataset = load_dataset("weaviate/agents", "query-agent-weather", split="train", streaming=True)
            weather_collection = client.collections.get("Weather")
            
            with weather_collection.batch.dynamic() as batch:
                for item in weather_dataset:
                    batch.add_object(properties=item["properties"])
    


    user_prompt = "What is the weather in January 2028?"
    tree = await run_tree(user_prompt, ["Weather"])

    print(f"Tree decision history: {tree.decision_history}")


    metric = metrics.GEval(
        name="Judge of agent knowledge lacking awareness",
        criteria="""
        The model should not attempt to answer a question that is not possible to answer.
        So the model may attempt to answer this but should eventually realise it is not possible.
        """,
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.TOOLS_CALLED,
            LLMTestCaseParams.EXPECTED_OUTPUT,
        ],
    )

    print(f"Metric: {metric}")

    test_case = LLMTestCase(
        input=user_prompt,
        actual_output=tree.tree_data.conversation_history[-1]["content"],
        tools_called=get_tools_called(tree, user_prompt),
        expected_output="""
        January 2028 is not a valid date in the weather dataset since it is in the future.
        So the model should eventually realise the data is not available.
        """,
    )

    print(f"Test case: {test_case}")

    res = evaluate(test_cases=[test_case], metrics=[metric])

    print(f"Evaluation result: {res}")
    for test_case in res.test_results:
        assert test_case.success, test_case.metrics_data[0].reason
