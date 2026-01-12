import logging
from copy import copy
from typing import Type

import dspy
from dspy.adapters.json_adapter import JSONAdapter
from dspy.primitives.module import Module
from dspy.signatures.signature import Signature, ensure_signature

from elysia.config import get_model_token_limits
from elysia.tree.objects import Atlas, TreeData
from elysia.util.client import ClientManager
from elysia.util.retrieve_feedback import retrieve_feedback
from elysia.util.token_manager import (
    get_context_truncator,
    get_token_counter,
)

elysia_meta_prompt = """
You are part of an ensemble of agents that are working together to solve a task.
Your task is just one as part of a larger system of agents designed to work together.
You will be given meta information about where you are in the larger system, 
such as what other tasks have been completed, any items or objects that have been collected during the full process.

Your job is not to answer the entire task, but to complete your part of the task.
Therefore the `user_prompt` should not be judged in its entirety, analyse what you can complete based on the prompt.
Complete this task only, remember that other agents will complete other parts of the task.
"""


class ElysiaChainOfThought(Module):
    """
    A custom reasoning DSPy module that reasons step by step in order to predict the output of a task.
    It will automatically include the most relevant inputs:
    - The user's prompt
    - The conversation history
    - The atlas
    - Any errors (from calls of the same tool)

    And you can also include optional inputs (by setting their boolean flags on initialisation to `True`):
    - The environment
    - The collection schemas
    - The tasks completed

    You can also specify `collection_names` to only include certain collections in the collection schemas.

    It will optionally output (by setting the boolean flags on initialisation to `True`):
    - The reasoning (model step by step reasoning)
    - A message update (if `message_update` is `True`), a brief 'update' message to the user.
    - Whether the task is impossible (boolean)

    You can use this module by calling the `.aforward()` method, passing all your *new* inputs as keyword arguments.
    You do not need to include keyword arguments for the other inputs, like the `environment`.

    Example:
    ```python
    my_module = ElysiaChainOfThought(
        signature=...,
        tree_data=...,
        message_update=True,
        environment=True,
        collection_schemas=True,
        tasks_completed=True,
    )
    my_module.aforward(input1=..., input2=..., lm=...)
    ```
    """

    def __init__(
        self,
        signature: Type[Signature],
        tree_data: TreeData,
        reasoning: bool = True,
        impossible: bool = True,
        message_update: bool = True,
        environment: bool = False,
        collection_schemas: bool = False,
        tasks_completed: bool = False,
        collection_names: list[str] = [],
        **config,
    ):
        """
        Args:
            signature (Type[dspy.Signature]): The signature of the module.
            tree_data (TreeData): Required. The tree data from the Elysia decision tree.
                Used to input the current state of the tree into the prompt.
                If you are using this module as part of a tool, the `tree_data` is an input to the tool call.
            reasoning (bool): Whether to include a reasoning input (chain of thought).
            impossible (bool): Whether to include a boolean flag indicating whether the task is impossible.
                This is useful for stopping the tree from continuing and returning to the base of the decision tree.
                For example, the model judges a query impossible to execute, or the user has not provided enough information.
            message_update (bool): Whether to include a message update input.
                If True, the LLM output will include a brief 'update' message to the user.
                This describes the current action the LLM is performing.
                Designed to increase interactivity and provide the user with information before the final output.
            environment (bool): Whether to include an environment input.
                If True, the module will include the currently stored data from previous tasks and actions into the prompt.
                This is useful so that the LLM knows what has already been done, and can avoid repeating actions.
                Or to use information from the environment to perform the new action.
            collection_schemas (bool): Whether to include a collection schema input.
                If True, the module will include the preprocessed collection schemas in the prompt input.
                This is useful so that the LLM knows the structure of the collections, if querying or similar.
                Use this sparingly, as it will use a large amount of tokens.
                You can specify `collection_names` to only include certain collections in this schema.
            tasks_completed (bool): Whether to include a tasks completed input.
                If True, the module will include the list of tasks completed input.
                This is a nicely formatted list of the tasks that have been completed, with the reasoning for each task.
                This is used so that the LLM has a 'stream of consciousness' of what has already been done,
                as well as to stop it from repeating actions.
                Other information is included in the `tasks_completed` field that format outputs from previous tasks.
                This is useful for continuing a decision logic across tasks, or to reinforce key information.
            collection_names (list[str]): A list of collection names to include in the prompt.
                If provided, this will modify the collection schema input to only include the collections in this list.
                This is useful if you only want to include certain collections in the prompt.
                And to reduce token usage.
            **config (Any): The DSPy configuration for the module.
        """

        super().__init__()

        signature = ensure_signature(signature)  # type: ignore

        # Create a shallow copy of the tree_data
        self.tree_data = copy(tree_data)

        # Note which inputs are required
        self.message_update = message_update
        self.environment = environment
        self.collection_schemas = collection_schemas
        self.tasks_completed = tasks_completed
        self.collection_names = collection_names
        self.reasoning = reasoning
        self.impossible = impossible

        # Initialize logger and token management utilities
        self.logger = logging.getLogger("rich")
        self.token_counter = get_token_counter()
        self.context_truncator = get_context_truncator()

        # == Inputs ==

        # -- User Prompt --
        user_prompt_desc = (
            "The user's original question/prompt that needs to be answered. "
            "This, possibly combined with the conversation history, will be used to determine your current action."
        )
        user_prompt_prefix = "${user_prompt}"
        user_prompt_field: str = dspy.InputField(
            prefix=user_prompt_prefix, desc=user_prompt_desc
        )

        # -- Conversation History --
        conversation_history_desc = (
            "Previous messages between user and assistant in chronological order: "
            "[{'role': 'user'|'assistant', 'content': str}] "
            "Use this to maintain conversation context and avoid repetition."
        )
        conversation_history_prefix = "${conversation_history}"
        conversation_history_field: list[dict] = dspy.InputField(
            prefix=conversation_history_prefix, desc=conversation_history_desc
        )

        # -- Atlas --
        atlas_desc = (
            "Your guide to how you should proceed as an agent in this task. "
            "This is pre-defined by the user."
        )
        atlas_prefix = "${atlas}"
        atlas_field: Atlas = dspy.InputField(prefix=atlas_prefix, desc=atlas_desc)

        # -- Errors --
        errors_desc = (
            "Any errors that have occurred during the previous attempt at this action. "
            "This is a list of dictionaries, containing details of the error. "
            "Make an attempt at providing different output to avoid this error now. "
            "If this error is repeated, or you judge it to be unsolvable, you can set `impossible` to True"
        )
        errors_prefix = "${previous_errors}"
        errors_field: list[dict] = dspy.InputField(
            prefix=errors_prefix, desc=errors_desc
        )

        # -- Add to Signature --
        extended_signature = signature.prepend(
            name="user_prompt", field=user_prompt_field, type_=str
        )
        extended_signature = extended_signature.append(
            name="conversation_history",
            field=conversation_history_field,
            type_=list[dict],
        )
        extended_signature = extended_signature.append(
            name="atlas", field=atlas_field, type_=Atlas
        )
        extended_signature = extended_signature.append(
            name="previous_errors", field=errors_field, type_=list[dict]
        )

        # == Optional Inputs / Outputs ==

        # -- Environment Input --
        if environment:
            environment_desc = (
                "Information gathered from completed tasks. "
                "Empty if no data has been retrieved yet. "
                "Use to determine if more information is needed. "
                "Additionally, use this as a reference to determine if you have already completed a task/what items are already available, to avoid repeating actions. "
                "All items here are already shown to the user, so do not repeat information from these fields unless summarising, providing extra information or otherwise. "
                "E.g., do not list out anything from here, only provide new content to the user."
            )
            environment_prefix = "${environment}"
            environment_field: dict = dspy.InputField(
                prefix=environment_prefix, desc=environment_desc
            )
            extended_signature = extended_signature.append(
                name="environment", field=environment_field, type_=dict
            )

        # -- Collection Schema Input --
        if collection_schemas:
            collection_schemas_desc = (
                "Metadata about available collections and their schemas: "
                "This is a dictionary with the following fields: "
                "{\n"
                "    name: collection name,\n"
                "    length: number of objects in the collection,\n"
                "    summary: summary of the collection,\n"
                "    fields: [\n"
                "        {\n"
                "            name: field_name,\n"
                "            groups: a dict with the value and count of each group.\n"
                "                a comprehensive list of all unique values that exist in the field.\n"
                "                if this is None, then no relevant groups were found.\n"
                "                these values are string, but the actual values in the collection are the 'type' of the field.\n"
                "            mean: mean of the field. if the field is text, this refers to the means length (in tokens) of the texts in this field. if the type is a list, this refers to the mean length of the lists,\n"
                "            range: minimum and maximum values of the length,\n"
                "            type: the data type of the field.\n"
                "        },\n"
                "        ...\n"
                "    ]\n"
                "}\n"
            )
            collection_schemas_prefix = "${collection_schemas}"
            collection_schemas_field: dict = dspy.InputField(
                prefix=collection_schemas_prefix, desc=collection_schemas_desc
            )
            extended_signature = extended_signature.append(
                name="collection_schemas", field=collection_schemas_field, type_=dict
            )

        # -- Tasks Completed Input --
        if tasks_completed:
            tasks_completed_desc = (
                "Which tasks have been completed in order. "
                "These are numbered so that higher numbers are more recent. "
                "Separated by prompts (so you should identify the prompt you are currently working on to see what tasks have been completed so far) "
                "Also includes reasoning for each task, to continue a decision logic across tasks. "
                "Use this to determine whether future searches, for this prompt are necessary, and what task(s) to choose. "
                "It is IMPORTANT that you separate what actions have been completed for which prompt, so you do not think you have failed an attempt for a different prompt."
            )
            tasks_completed_prefix = "${tasks_completed}"
            tasks_completed_field: str = dspy.InputField(
                prefix=tasks_completed_prefix, desc=tasks_completed_desc
            )
            extended_signature = extended_signature.append(
                name="tasks_completed", field=tasks_completed_field, type_=str
            )

        # -- Impossible Field --
        if impossible:
            impossible_desc = (
                "Given the actions you have available, and the environment/information. "
                "Is the task impossible to complete? "
                "I.e., do you wish that you had a different task to perform/choose from and hence should return to the base of the decision tree?"
                "Do not base this judgement on the entire prompt, as it is possible that other agents can perform other aspects of the request."
                "Do not judge impossibility based on if tasks have been completed, only on the current action and environment."
            )
            impossible_prefix = "${impossible}"
            impossible_field: bool = dspy.OutputField(
                prefix=impossible_prefix, desc=impossible_desc
            )
            extended_signature = extended_signature.prepend(
                name="impossible", field=impossible_field, type_=bool
            )

        # -- Message Update Output --
        if message_update:
            message_update_desc = (
                "Continue your current message to the user "
                "(latest assistant field in conversation history) with ONE concise sentence that: "
                "- Describes NEW technical details about your latest action "
                "- Highlights specific parameters or logic you just applied "
                "- Avoids repeating anything from conversation history "
                "- Speaks directly to them (no 'the user'), gender neutral message "
                "Just provide the new sentence update, not the full message from the conversation history. "
                "Your response should be based on only the part of the user's request that you can work on. "
                "It is possible other agents can perform other aspects of the request, so do not respond as if you cannot complete the entire request."
            )

            message_update_prefix = "${message_update}"
            message_update_field: str = dspy.OutputField(
                prefix=message_update_prefix, desc=message_update_desc
            )
            extended_signature = extended_signature.prepend(
                name="message_update", field=message_update_field, type_=str
            )

        # -- Reasoning Field --
        if reasoning:
            reasoning_desc = (
                "Reasoning: Repeat relevant parts of the any context within your environment, "
                "Evaluate all relevant information from the inputs, including any previous errors if applicable, "
                "use this to think step by step in order to answer the query."
                "Limit your reasoning to maximum 150 words. Only exceed this if the task is very complex."
            )
            reasoning_prefix = "${reasoning}"
            reasoning_field: str = dspy.OutputField(
                prefix=reasoning_prefix, desc=reasoning_desc
            )
            extended_signature = extended_signature.prepend(
                name="reasoning", field=reasoning_field, type_=str
            )

        # -- Predict --
        self.predict = dspy.Predict(extended_signature, **config)
        self.predict.signature.instructions += elysia_meta_prompt  # type: ignore

    def _add_tree_data_inputs(self, kwargs: dict, model_name: str):
        """
        Add tree data inputs to kwargs with token management and context truncation.
        Ensures the total context stays within safe token limits for the model.

        Args:
            kwargs (dict): The keyword arguments dictionary to populate
            model_name (str): The model name to use for token counting and limits

        Returns:
            dict: The kwargs dictionary with added tree data inputs
        """
        # Get the safe token limit for this model
        context_window, max_output_tokens, safe_input_limit = get_model_token_limits(
            model_name
        )

        # Reserve tokens for output and overhead
        # Allocate 70% of safe input limit for actual context to be conservative
        max_context_tokens = int(safe_input_limit * 0.7)

        # Add the tree data inputs to the kwargs
        kwargs["user_prompt"] = self.tree_data.user_prompt
        kwargs["atlas"] = self.tree_data.atlas
        kwargs["previous_errors"] = self.tree_data.get_errors()

        # Truncate conversation history to fit within token limits
        # Conversation history can grow unbounded, so truncate aggressively
        conversation_history = self.tree_data.conversation_history
        max_conversation_tokens = int(max_context_tokens * 0.3)  # 30% of context
        truncated_conversation = self.context_truncator.truncate_conversation_history(
            conversation_history,
            max_tokens=max_conversation_tokens,
            model=model_name,
            keep_first=1,  # Keep system message
            keep_last=5,  # Keep last 5 messages for recent context
        )
        kwargs["conversation_history"] = truncated_conversation

        if (
            len(truncated_conversation) < len(conversation_history)
            and len(conversation_history) > 0
        ):
            self.logger.warning(
                f"Truncated conversation history from {len(conversation_history)} "
                f"to {len(truncated_conversation)} messages to fit token limit"
            )

        # Add the optional inputs to the kwargs with truncation
        if self.environment:
            environment_data = self.tree_data.environment.environment
            max_environment_tokens = int(max_context_tokens * 0.2)  # 20% of context
            truncated_environment = self.context_truncator.truncate_dict(
                environment_data, max_tokens=max_environment_tokens, model=model_name
            )
            kwargs["environment"] = truncated_environment

            if len(truncated_environment) < len(environment_data):
                self.logger.warning(
                    f"Truncated environment from {len(environment_data)} "
                    f"to {len(truncated_environment)} keys to fit token limit"
                )

        if self.collection_schemas:
            if self.collection_names != []:
                collection_schemas = self.tree_data.output_collection_metadata(
                    collection_names=self.collection_names, with_mappings=False
                )
            else:
                collection_schemas = self.tree_data.output_collection_metadata(
                    with_mappings=False
                )

            # Collection schemas can be very large, allocate 40% of context for schemas
            # (increased from 25% to accommodate large chunk collection schemas with geocoded data)
            max_schema_tokens = int(max_context_tokens * 0.40)
            truncated_schemas = self.context_truncator.truncate_dict(
                collection_schemas, max_tokens=max_schema_tokens, model=model_name
            )
            kwargs["collection_schemas"] = truncated_schemas

            if len(truncated_schemas) < len(collection_schemas):
                self.logger.warning(
                    f"Truncated collection schemas from {len(collection_schemas)} "
                    f"to {len(truncated_schemas)} collections to fit token limit"
                )

        if self.tasks_completed:
            tasks_completed_str = self.tree_data.tasks_completed_string()
            max_tasks_tokens = int(max_context_tokens * 0.15)  # 15% of context

            # Count tokens and truncate if necessary
            tasks_tokens = self.token_counter.count_tokens(
                tasks_completed_str, model=model_name
            )
            if tasks_tokens > max_tasks_tokens:
                self.logger.warning(
                    f"Tasks completed string is too large ({tasks_tokens} tokens). "
                    f"Truncating to {max_tasks_tokens} tokens"
                )
                # Truncate from the beginning, keeping recent tasks
                # Estimate characters per token (~4) and truncate accordingly
                target_chars = max_tasks_tokens * 4
                if len(tasks_completed_str) > target_chars:
                    truncated_str = (
                        "... [earlier tasks truncated] ...\n"
                        + tasks_completed_str[-target_chars:]
                    )
                    kwargs["tasks_completed"] = truncated_str
                else:
                    kwargs["tasks_completed"] = tasks_completed_str
            else:
                kwargs["tasks_completed"] = tasks_completed_str

        # Log total estimated token usage
        total_tokens = 0
        for key, value in kwargs.items():
            token_count = self.token_counter.count_tokens(str(value), model=model_name)
            total_tokens += token_count

        if total_tokens > safe_input_limit:
            self.logger.error(
                f"Total context tokens ({total_tokens}) exceeds safe input limit ({safe_input_limit}) "
                f"for model {model_name}. Further truncation may be needed."
            )
        else:
            self.logger.debug(
                f"Total context tokens: {total_tokens}/{safe_input_limit} "
                f"({(total_tokens / safe_input_limit) * 100:.1f}% of safe limit)"
            )

        return kwargs

    def forward(self, **kwargs):
        # Extract model name from the LM object if provided
        model_name = self._get_model_name_from_kwargs(kwargs)
        kwargs = self._add_tree_data_inputs(kwargs, model_name)

        # Use JSONAdapter for GPT-5 models with Responses API
        # This ensures structured outputs (like List[TextWithCitation]) are parsed correctly
        lm = kwargs.get("lm")
        if lm and hasattr(lm, "model_type") and lm.model_type == "responses":
            # GPT-5 models use Responses API which returns JSON format
            # JSONAdapter is needed to parse the JSON response into structured objects
            with dspy.settings.context(adapter=JSONAdapter()):
                return self.predict(**kwargs)

        return self.predict(**kwargs)

    async def aforward(self, **kwargs):
        # Extract model name from the LM object if provided
        model_name = self._get_model_name_from_kwargs(kwargs)
        kwargs = self._add_tree_data_inputs(kwargs, model_name)

        # Use JSONAdapter for GPT-5 models with Responses API
        # This ensures structured outputs (like List[TextWithCitation]) are parsed correctly
        lm = kwargs.get("lm")
        if lm and hasattr(lm, "model_type") and lm.model_type == "responses":
            # GPT-5 models use Responses API which returns JSON format
            # JSONAdapter is needed to parse the JSON response into structured objects
            with dspy.settings.context(adapter=JSONAdapter()):
                return await self.predict.acall(**kwargs)

        return await self.predict.acall(**kwargs)

    def _get_model_name_from_kwargs(self, kwargs: dict) -> str:
        """
        Extract the model name from the kwargs.
        The LM object is passed as 'lm' in kwargs.

        Args:
            kwargs (dict): The keyword arguments containing the LM object

        Returns:
            str: The model name, defaulting to 'gpt-5' if not found
        """
        lm = kwargs.get("lm")
        if lm and hasattr(lm, "model"):
            return lm.model
        elif lm and hasattr(lm, "kwargs") and "model" in lm.kwargs:
            return lm.kwargs["model"]
        else:
            # Default to gpt-5 if model name cannot be extracted
            self.logger.warning(
                "Could not extract model name from LM object. Using default 'gpt-5'"
            )
            return "gpt-5"

    async def aforward_with_feedback_examples(
        self,
        feedback_model: str,
        client_manager: ClientManager,
        base_lm: dspy.LM,
        complex_lm: dspy.LM,
        num_base_lm_examples: int = 3,
        return_example_uuids: bool = False,
        **kwargs,
    ) -> tuple[dspy.Prediction, list[str]] | dspy.Prediction:
        """
        Use the forward pass of the module with feedback examples.
        This will first retrieve examples from the feedback collection, and use those as few-shot examples to run the module.
        It retrieves based from vectorising and searching on the user's prompt, finding similar prompts from the feedback collection.
        This is an EXPERIMENTAL feature, and may not work as expected.

        If the number of examples is less than `num_base_lm_examples`, the module will use the complex LM.
        Otherwise, it will use the base LM. This is so that the less accurate, but faster base LM can be used when guidance is available.
        However, when there are insufficient examples, the complex LM will be used.

        Args:
            feedback_model (str): The label of the feedback data to use as examples.
                E.g., "decision" is the default name given to examples for the LM in the decision tree.
                This is used to retrieve the examples from the feedback collection.
            client_manager (ClientManager): The client manager to use.
            base_lm (dspy.LM): The base LM to (conditionally) use.
            complex_lm (dspy.LM): The complex LM to (conditionally) use.
            num_base_lm_examples (int): The threshold number of examples to use the base LM.
                When there are fewer examples than this, the complex LM will be used.
            **kwargs (Any): The keyword arguments to pass to the forward pass.
                Important: All additional inputs to the DSPy module should be passed here as keyword arguments.
                Also: Do not include `lm` in the kwargs, as this will be set automatically.

        Returns:
            (dspy.Prediction): The prediction from the forward pass.
        """

        examples, uuids = await retrieve_feedback(
            client_manager, self.tree_data.user_prompt, feedback_model, n=10
        )
        if len(examples) > 0:
            optimizer = dspy.LabeledFewShot(k=10)
            optimized_module = optimizer.compile(self, trainset=examples)
        else:
            if return_example_uuids:
                return (
                    await self.aforward(lm=complex_lm, **kwargs),
                    uuids,
                )
            else:
                return await self.aforward(lm=complex_lm, **kwargs)

        # Select the LM to use based on the number of examples
        if len(examples) < num_base_lm_examples:
            if return_example_uuids:
                return (
                    await optimized_module.aforward(lm=complex_lm, **kwargs),
                    uuids,
                )
            else:
                return await optimized_module.aforward(lm=complex_lm, **kwargs)
        else:
            if return_example_uuids:
                return (
                    await optimized_module.aforward(lm=base_lm, **kwargs),
                    uuids,
                )
            else:
                return await optimized_module.aforward(lm=base_lm, **kwargs)
