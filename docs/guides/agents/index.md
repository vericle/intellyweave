# Agents and Domain Router

**Specialized tools and intelligent query routing for domain-specific intelligence analysis.**

## What It Does

IntellyWeave's agent system provides two capabilities:

1. **Domain Router**: Classifies user queries and routes them to appropriate specialized agents
2. **Specialized Agents**: System and custom agents that handle domain-specific queries

```text
User Query → Domain Router → Classification → Specialized Agent → Response
```

This system enables:

- **Automatic routing** to the right agent based on query intent
- **Custom agents** with user-defined knowledge bases
- **System agents** for common tasks (entity extraction, geocoding, personalization)
- **Decision tree integration** where agents act as Tools

## Use When

- You need specialized handling for specific query types
- You want to create custom agents with dedicated knowledge bases
- You need entity extraction, geocoding, or personalization
- You want automatic routing without manual agent selection

## Agent Categories

IntellyWeave has two categories of agents:

### System Agents (Option A: Decision Tree Tools)

Always-available tools that the decision tree can invoke directly:

| Agent | Purpose | Inputs |
|-------|---------|--------|
| **QueryExtractorTool** | Extracts and enriches entities from documents | `query`, `documents` |
| **GeospatialTransformationTool** | Geocodes locations and creates virtual documents | `entities`, `user_interest`, `operation_mode` |
| **PersonalizationTool** | Adjusts workflow based on user preferences | `query`, `user_id` |

### Custom User Agents (Option B: Router-Accessible)

User-defined agents that the Domain Router can select:

| Agent | Purpose | Selection Criteria |
|-------|---------|-------------------|
| **PersonalizationAgent** | Workflow customization via router | Query involves preferences |
| **Custom Agents** | User-uploaded knowledge bases | Query matches agent domain |

## How the System Works

### Query Flow

```text
1. User submits query
2. Domain Router analyzes query intent
3. Router classifies into domain (agent name or "not-related")
4. Classification stored in hidden_environment
5. Matching agent's is_tool_available() returns True
6. Agent processes query and returns response
```

### Router Classification

The Domain Router evaluates queries once per session:

```python
# Router stores classification in hidden_environment
tree_data.environment.hidden_environment["domain_classification"] = {
    "domain": "Personalization Agent",  # or "not-related"
    "reasoning": "Query involves workflow customization",
    "confidence": "high"
}
```

### Agent Selection

Each agent implements `is_tool_available()` to check if it should handle the query:

```python
async def is_tool_available(self, tree_data, ...):
    classification = tree_data.environment.hidden_environment.get(
        "domain_classification", {}
    )
    return classification.get("domain") == self.agent_name
```

## System Agents

### QueryExtractorTool

Extracts and enriches entities from documents using GLiNER metadata.

**File**: `backend/elysia/agents/query_extractor.py`

**Purpose**: On-demand entity extraction from specific queries or documents.

**Key Features**:
- Reads GLiNER entities from document metadata
- Uses LLM to enrich and contextualize entities
- Finds source references and co-occurrences
- Works with documents from previous query results

**Usage**:
```python
inputs = {
    "query": "Who are the key people mentioned?",
    "documents": [...]  # Optional - reads from environment if not provided
}
```

**Output**: Structured findings with entity type, description, confidence, and reasoning.

---

### GeospatialTransformationTool

Enriches entities with geographic coordinates and creates virtual location documents.

**File**: `backend/elysia/agents/geo_transformer.py`

**Purpose**: Add geocoding to entities and persist locations as searchable documents.

**Operation Modes**:

| Mode | Description |
|------|-------------|
| `geocode` | Enrich entities with coordinates (in-memory, no persistence) |
| `persist` | Save locations as virtual documents in Weaviate |

**Key Features**:
- Uses LLM to filter relevant locations based on user interest
- Geocodes using external geocoding service
- Creates virtual documents for locations not in the knowledge base
- Generates minimal, factual location descriptions

**Usage**:
```python
inputs = {
    "operation_mode": "geocode",  # or "persist"
    "entities": [...],
    "user_interest": "Show me military bases in Germany",
    "user_id": "user123"  # Required for persist mode
}
```

---

### PersonalizationTool

Adjusts workflow parameters based on user intent and profile.

**File**: `backend/elysia/agents/personalization.py`

**Purpose**: Tailor analysis parameters to user-specific needs.

**Key Features**:
- Analyzes user intent from query
- Fetches user profile (role, preferences, history)
- Recommends workflow adjustments
- Returns configuration for downstream processing

**Intent Categories**:
- `historical_research` - Deep archival analysis
- `quick_intel` - Fast, summary-focused queries
- `legal_analysis` - Structured legal examination
- `geospatial_exploration` - Location-focused queries

**Usage**:
```python
inputs = {
    "query": "Give me a comprehensive analysis of Cold War documents",
    "user_id": "user123"
}
```

**Output**: Workflow configuration with intent, reasoning, and settings.

---

### PersonalizationAgent

Router-accessible version of personalization for automatic selection.

**File**: `backend/elysia/agents/personalization.py`

**Purpose**: Same as PersonalizationTool but selectable by Domain Router.

**Selection Criteria**:
Queries involving:
- Workflow customization
- User preference adaptation
- Personalized analysis approaches

## Custom User Agents

Users can create custom agents with dedicated knowledge bases.

### How Custom Agents Work

1. **User uploads document** to create knowledge base
2. **User defines agent** with name, description, and system prompt
3. **Agent metadata stored** in Weaviate
4. **CustomAgentRegistry loads** agents on session start
5. **Domain Router includes** custom agents in classification
6. **CustomAgentFactory creates** Tool instances dynamically

### Custom Agent Structure

```python
agent_metadata = {
    "agent_id": "uuid-here",
    "agent_name": "Immigration Law Expert",
    "agent_description": "Specializes in immigration law questions",
    "system_prompt": "You are an expert in immigration law...",
    "document_id": "uuid-of-knowledge-base-document",
    "user_id": "owner-user-id"
}
```

### Custom Agent Execution

When selected by the router:

1. **Query knowledge base** - Hybrid search on agent's document chunks
2. **Retrieve relevant chunks** - Top 5 chunks by relevance
3. **Generate response** - Using system prompt and retrieved context
4. **Return with citations** - TextWithCitations linking to source chunks

## Architecture

### Backend Structure

```text
backend/elysia/
├── agents/                           # System specialized agents
│   ├── __init__.py                  # Exports all agents
│   ├── query_extractor.py           # QueryExtractorTool
│   ├── geo_transformer.py           # GeospatialTransformationTool
│   └── personalization.py           # PersonalizationTool, PersonalizationAgent
└── tools/domain/                     # Domain routing system
    ├── router.py                    # DomainRouter Tool
    ├── custom_agent_registry.py     # Loads and manages custom agents
    ├── custom_agent_factory.py      # Creates custom agent Tool instances
    ├── custom_agent_store.py        # Weaviate storage for agent metadata
    ├── prompt_templates.py          # Dynamic prompt generation
    └── objects.py                   # DomainClassification, DomainResponse
```

### Data Flow

```text
Session Start
    │
    ▼
CustomAgentRegistry.load_custom_agents()
    │
    ├── Load user's custom agents from Weaviate
    ├── Add system agents (QueryExtractor, Geospatial, Personalization)
    └── Add router-accessible agents (PersonalizationAgent)
    │
    ▼
User Query
    │
    ▼
DomainRouter.__call__()
    │
    ├── Get custom agent names and descriptions
    ├── Create dynamic classification prompt
    ├── Classify query via LLM
    └── Store classification in hidden_environment
    │
    ▼
Decision Tree Iteration
    │
    ├── Each agent checks is_tool_available()
    ├── Matching agent returns True
    └── Agent processes query
```

## Troubleshooting

### Router Always Returns "not-related"

**Cause**: No custom agents loaded or query doesn't match agent descriptions.

**Solution**:
- Verify custom agents are loaded: Check registry logs
- Improve agent descriptions to better match query patterns

### Custom Agent Can't Find Documents

**Cause**: Document chunks not in expected collection or wrong document_id.

**Solution**:
- Verify collection exists: `ELYSIA_CHUNKED_elysia_uploaded_documents__`
- Check document_id in agent metadata matches uploaded document

### PersonalizationAgent Not Selected

**Cause**: Query doesn't trigger personalization domain classification.

**Solution**: Include explicit personalization keywords in query (e.g., "customize", "preferences", "tailor").

### GeospatialTransformationTool Returns Empty

**Cause**: No entities have location type or LLM filtered all as irrelevant.

**Solution**:
- Verify entities include location-type items
- Make user_interest more specific to match locations

## See Also

- [Domain Router Documentation](domain-router.md) - Detailed router behavior
- [Custom Agents](custom-agents.md) - Creating and managing custom agents
- [Intelligence Analysis](../intelligence-analysis/) - Multi-agent orchestration
- [Courthouse Debate](../courthouse-debate/) - Adversarial multi-agent system
