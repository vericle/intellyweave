# ABOUTME: Factory for dynamically generating custom agent Tool classes
# ABOUTME: Creates Tool instances from agent metadata stored in Weaviate

import logging
from logging import Logger
from typing import Any, AsyncGenerator

import dspy
from weaviate.classes.query import Filter

from elysia.objects import Error, Result, Status, Tool
from elysia.tools.text.objects import TextWithCitation, TextWithCitations
from elysia.tree.objects import TreeData
from elysia.util.client import ClientManager
from elysia.util.elysia_chain_of_thought import ElysiaChainOfThought

module_logger = logging.getLogger(__name__)


class CustomAgentPrompt(dspy.Signature):
    """
    Signature for custom agent responses.

    The agent uses its system prompt and retrieved knowledge base
    to provide expert responses to user queries.
    """

    system_prompt = dspy.InputField(
        desc="System instructions defining the agent's behavior and expertise"
    )
    user_prompt = dspy.InputField(desc="The user's query")
    retrieved_documents = dspy.InputField(
        desc="Relevant documents retrieved from the agent's knowledge base"
    )

    response = dspy.OutputField(
        desc="A comprehensive response to the user's query, following the system prompt instructions and grounded in the retrieved documents"
    )


class CustomAgentFactory:
    """
    Factory for creating custom agent Tool instances.

    Generates Tool subclasses dynamically based on agent metadata,
    allowing users to create specialized agents with custom knowledge bases.
    """

    @staticmethod
    def create_agent(
        agent_metadata: dict[str, Any],
        collection_name: str = "ELYSIA_CHUNKED_elysia_uploaded_documents__",
        logger: Logger | None = None,
    ) -> Tool:
        """
        Create a custom agent Tool instance from metadata.

        Args:
            agent_metadata: Dictionary containing agent configuration:
                - agent_id: Unique identifier
                - agent_name: Human-readable name
                - system_prompt: Agent behavior instructions
                - document_id: UUID of knowledge base document
                - agent_description: Description for routing
                - user_id: Owner user ID
            collection_name: Weaviate collection containing document chunks
            logger: Optional logger for debug output

        Returns:
            Tool instance representing the custom agent
        """

        agent_id = agent_metadata["agent_id"]
        agent_name = agent_metadata["agent_name"]
        system_prompt = agent_metadata["system_prompt"]
        document_id = agent_metadata["document_id"]
        agent_description = agent_metadata["agent_description"]

        class DynamicCustomAgent(Tool):
            """
            Dynamically generated custom agent Tool.

            Queries its dedicated knowledge base and responds according
            to the user-defined system prompt.
            """

            def __init__(self, **kwargs) -> None:
                super().__init__(
                    name=agent_name,
                    description=agent_description,
                    status=f"Consulting {agent_name} knowledge base...",
                    inputs={},
                    end=True,
                    **kwargs,
                )
                self.agent_id = agent_id
                self.agent_name = agent_name
                self.system_prompt = system_prompt
                self.document_id = document_id
                self.collection_name = collection_name
                self.logger = logger or module_logger
                if self.logger:
                    self.logger.debug(
                        "Initialized custom agent %s (id=%s, document=%s)",
                        self.agent_name,
                        self.agent_id,
                        self.document_id,
                    )

            async def is_tool_available(
                self,
                tree_data: TreeData,
                base_lm: dspy.LM,
                complex_lm: dspy.LM,
                client_manager: ClientManager,
                **kwargs,
            ) -> bool:
                """
                Check if this agent should handle the current query.

                Available if:
                1. Router classified query as this agent's domain, OR
                2. Agent name/ID mentioned in classification
                """
                classification = tree_data.environment.hidden_environment.get(
                    "domain_classification", {}
                )

                if self.logger and classification:
                    self.logger.debug(
                        "Custom agent %s received classification payload: %s",
                        self.agent_name,
                        classification,
                    )

                classified_domain = classification.get("domain", "")

                # Check if classified as this custom agent
                # Domain router will set domain to custom agent name if matched
                return (
                    classified_domain == self.agent_name
                    or classified_domain == f"custom_agent_{self.agent_id}"
                    or classified_domain == self.agent_id
                )

            async def __call__(
                self,
                tree_data: TreeData,
                inputs: dict,
                base_lm: dspy.LM,
                complex_lm: dspy.LM,
                client_manager: ClientManager,
                **kwargs,
            ) -> AsyncGenerator:
                """
                Process user query using custom agent knowledge base.

                Retrieves relevant chunks from the agent's document,
                then generates response using system prompt.
                """
                if self.logger:
                    self.logger.debug(f"Custom Agent '{self.agent_name}' called!")
                    self.logger.debug(
                        "User prompt preview (chars=%s): %s",
                        len(tree_data.user_prompt),
                        tree_data.user_prompt[:200],
                    )

                yield Status(f"Searching {self.agent_name} knowledge base...")

                # Retrieve document chunks
                retrieved_docs = []
                retrieved_text = ""

                try:
                    async with client_manager.connect_to_async_client() as client:
                        # Check if chunked collection exists
                        if not await client.collections.exists(self.collection_name):
                            if self.logger:
                                self.logger.warning(
                                    f"Collection '{self.collection_name}' not found. "
                                    "Providing response without knowledge base."
                                )
                            yield Status(
                                f"{self.agent_name} knowledge base not available. "
                                "Providing general guidance..."
                            )
                            retrieved_text = f"No knowledge base documents available for {self.agent_name}."
                        else:
                            collection = client.collections.get(self.collection_name)

                            # Query chunks filtered by document_id via reference
                            # Chunks are linked to parent documents via "fullDocument" reference
                            # We need to filter chunks where fullDocument points to our document_id
                            self.logger.debug(
                                "Querying collection %s for document_id=%s",
                                self.collection_name,
                                self.document_id,
                            )

                            response = await collection.query.hybrid(
                                query=tree_data.user_prompt,
                                limit=5,
                                return_metadata=["score"],
                                filters=Filter.by_ref("fullDocument")
                                .by_id()
                                .equal(self.document_id),
                            )

                            if self.logger:
                                self.logger.debug(
                                    f"Retrieved {len(response.objects)} chunks from {self.agent_name} knowledge base"
                                )

                            # Extract chunks
                            for obj in response.objects:
                                doc_dict = dict(obj.properties)
                                doc_dict["uuid"] = str(obj.uuid)
                                doc_dict["score"] = (
                                    obj.metadata.score if obj.metadata else None
                                )
                                retrieved_docs.append(doc_dict)

                            # Format chunks for prompt
                            if retrieved_docs:
                                retrieved_text = "\n\n".join(
                                    [
                                        f"Chunk {i + 1}:\n"
                                        f"{doc.get('content', doc.get('text', 'No content'))}"
                                        for i, doc in enumerate(retrieved_docs)
                                    ]
                                )
                                yield Status(
                                    f"Found {len(retrieved_docs)} relevant chunks from {self.agent_name} knowledge base..."
                                )
                            else:
                                retrieved_text = f"No relevant documents found in {self.agent_name} knowledge base for this query."
                                yield Status(
                                    "No specific documents found. Providing general guidance based on system instructions..."
                                )

                except Exception as e:
                    if self.logger:
                        self.logger.exception(
                            "Error querying %s knowledge base", self.agent_name
                        )
                    yield Error(
                        error_message=f"Failed to query {self.agent_name} knowledge base: {str(e)}"
                    )
                    return

                # Yield retrieved chunks as Result so they get _REF_ID for citations
                if retrieved_docs:
                    yield Status(
                        f"Retrieved {len(retrieved_docs)} chunks from knowledge base..."
                    )

                    # Prepare chunks for Result
                    chunk_objects = []
                    for i, doc in enumerate(retrieved_docs):
                        chunk_objects.append(
                            {
                                "content": doc.get(
                                    "content", doc.get("text", "No content")
                                ),
                                "score": doc.get("score"),
                                "title": doc.get("title", "Untitled Document"),
                                "author": doc.get("author", "Unknown Author"),
                                "chunk_number": i + 1,
                            }
                        )

                    # Yield chunks as Result so they get _REF_ID values
                    yield Result(
                        objects=chunk_objects,
                        metadata={
                            "source": f"{self.agent_name} Knowledge Base",
                            "total_chunks": len(retrieved_docs),
                        },
                        payload_type="document",
                        name=f"{self.agent_name}_chunks",
                    )

                # Generate response using system prompt
                yield Status(f"Generating {self.agent_name} response...")

                try:
                    response_generator = ElysiaChainOfThought(
                        CustomAgentPrompt,
                        tree_data=tree_data,
                        reasoning=False,
                        impossible=False,
                        environment=False,
                        tasks_completed=False,
                        message_update=False,
                    )

                    response_output = await response_generator.aforward(
                        lm=complex_lm,
                        system_prompt=self.system_prompt,
                        user_prompt=tree_data.user_prompt,
                        retrieved_documents=retrieved_text,
                    )

                    # Handle both dict and object response formats
                    if isinstance(response_output, dict):
                        response_text = response_output.get(
                            "response", str(response_output)
                        )
                    else:
                        response_text = getattr(
                            response_output, "response", str(response_output)
                        )

                    if self.logger:
                        self.logger.debug(
                            "Generated response for %s (chars=%s)",
                            self.agent_name,
                            len(response_text),
                        )

                    # Create proper TextWithCitation objects for chunk-level citations
                    # Each citation references the chunks via their _REF_ID values
                    if retrieved_docs:
                        # Get the ref_ids for the chunks we just yielded
                        # They will be in the environment with sequential _REF_IDs
                        chunk_ref_ids = [str(i + 1) for i in range(len(retrieved_docs))]

                        # Create a single TextWithCitation with the response referencing all chunks
                        cited_texts = [
                            TextWithCitation(
                                text=response_text,
                                ref_ids=chunk_ref_ids,
                            )
                        ]
                    else:
                        # No chunks retrieved, just return response without citations
                        cited_texts = [
                            TextWithCitation(
                                text=response_text,
                                ref_ids=[],
                            )
                        ]

                    # Yield final response with citations
                    yield TextWithCitations(
                        cited_texts=cited_texts,
                        title=f"{self.agent_name} Response",
                    )

                    if self.logger:
                        self.logger.debug(
                            f"Custom Agent '{self.agent_name}' completed successfully!"
                        )

                except Exception as e:
                    if self.logger:
                        self.logger.exception(
                            "Error generating %s response", self.agent_name
                        )
                    yield Error(
                        error_message=f"Failed to generate {self.agent_name} response: {str(e)}"
                    )

        # Return instance of the dynamically created class
        return DynamicCustomAgent(logger=logger)
