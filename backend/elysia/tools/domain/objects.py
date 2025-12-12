# ABOUTME: Result objects for domain-specific agents and router
# ABOUTME: Defines classification results and domain-specific response types

from elysia.objects import Result


class DomainClassification(Result):
    """
    Result object for domain router classification.
    Stores the classified domain and reasoning for the classification.
    """

    def __init__(
        self,
        domain: str,
        reasoning: str,
        confidence: str = "high",
    ):
        """
        Args:
            domain (str): The classified domain. One of: "immigration-law", "parent-law", "construction-law", "not-related"
            reasoning (str): The reasoning behind the classification
            confidence (str): Confidence level of the classification. One of: "high", "medium", "low"
        """
        super().__init__(
            objects=[
                {
                    "domain": domain,
                    "reasoning": reasoning,
                    "confidence": confidence,
                }
            ],
            metadata={
                "domain": domain,
                "reasoning": reasoning,
                "confidence": confidence,
            },
            name="domain_classification",
        )
        self.domain = domain
        self.reasoning = reasoning
        self.confidence = confidence

    def llm_parse(self) -> str:
        """
        Format classification result for LLM consumption.
        """
        return f"Query classified as: {self.domain}. Reasoning: {self.reasoning}"


class DomainResponse(Result):
    """
    Result object for domain-specific agent responses.
    Contains the response text with citations from domain knowledge base.
    """

    def __init__(
        self,
        response_text: str,
        citations: list[dict],
        domain: str,
        collection_name: str,
    ):
        """
        Args:
            response_text (str): The main response text
            citations (list[dict]): List of citations with source documents
            domain (str): The domain this response is for
            collection_name (str): The Weaviate collection queried
        """
        super().__init__(
            objects=citations,
            metadata={
                "domain": domain,
                "collection_name": collection_name,
                "response_text": response_text,
                "num_citations": len(citations),
            },
            name=f"{domain}_response",
        )
        self.response_text = response_text
        self.citations = citations
        self.domain = domain

    def llm_parse(self) -> str:
        """
        Format domain response for LLM consumption.
        """
        citation_text = "\n".join(
            [
                f"- {cite.get('title', 'Untitled')}: {cite.get('excerpt', '')}"
                for cite in self.citations
            ]
        )
        return f"Domain response for {self.domain}:\n{self.response_text}\n\nCitations:\n{citation_text}"
