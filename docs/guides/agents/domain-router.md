# Domain Router

**Intelligent query classification that routes user queries to specialized agents.**

## What It Does

The Domain Router is a Tool that:

1. Analyzes user query intent
2. Classifies into a domain (agent name or "not-related")
3. Stores classification for downstream agents
4. Runs once per query to prevent infinite loops

```text
User Query → Domain Router → Classification → Agent Selection
```

## Use When

The Domain Router is automatically invoked when:

- Custom agents are available for the user
- Query may require specialized knowledge
- Decision tree evaluates available tools

## How It Works

### Classification Flow

```text
1. Router receives user query
2. Loads custom agent names and descriptions from hidden_environment
3. Creates dynamic prompt with available domains
4. LLM classifies query into one domain
5. Stores classification in hidden_environment
6. Subsequent agents check classification
```

### One-Time Execution

The router only runs once per query:

```python
async def is_tool_available(self, tree_data, ...):
    # Check if classification already exists
    classification_exists = (
        "domain_classification" in tree_data.environment.hidden_environment
    )
    # Only available if no classification yet
    return not classification_exists
```

This prevents infinite loops where the router would run on every decision tree iteration.

## Classification Output

The router produces a `DomainClassification` result:

```python
DomainClassification(
    domain="Immigration Law Expert",  # or "not-related"
    reasoning="Query asks about visa requirements which matches Immigration Law Expert",
    confidence="high"  # or "medium", "low"
)
```

### Storage Location

Classification is stored in `hidden_environment`:

```python
tree_data.environment.hidden_environment["domain_classification"] = {
    "domain": "Immigration Law Expert",
    "reasoning": "Query asks about visa requirements...",
    "confidence": "high"
}
```

### Valid Domains

The router dynamically builds valid domains from:

1. `"not-related"` - Default for general queries
2. Custom agent names loaded from registry
3. System router-accessible agents (e.g., PersonalizationAgent)

## Dynamic Prompt Generation

The router creates a custom DSPy signature based on available agents:

```python
# From prompt_templates.py
DynamicPrompt = create_domain_router_prompt(
    custom_agent_names=["Immigration Expert", "Tax Advisor"],
    custom_agent_descriptions={
        "Immigration Expert": "Specializes in visa and immigration questions",
        "Tax Advisor": "Handles tax law and compliance questions"
    }
)
```

### Generated Prompt Structure

The dynamic prompt includes:

```text
You are a query classifier. Analyze the user's query and determine which
specialized agent should handle it.

Available domains:
- not-related: General queries that don't need specialized handling
- Immigration Expert: Specializes in visa and immigration questions
- Tax Advisor: Handles tax law and compliance questions

Classify the following query into exactly ONE domain.
```

## Agent Integration

### How Agents Use Classification

Each router-accessible agent implements `is_tool_available()`:

```python
async def is_tool_available(self, tree_data, ...):
    classification = tree_data.environment.hidden_environment.get(
        "domain_classification", {}
    )
    classified_domain = classification.get("domain", "").lower()

    # Check if classified as this agent
    return classified_domain == self.agent_name.lower()
```

### Custom Agent Matching

Custom agents match on multiple criteria:

```python
return (
    classified_domain == self.agent_name  # Exact name match
    or classified_domain == f"custom_agent_{self.agent_id}"  # ID prefix
    or classified_domain == self.agent_id  # Direct ID match
)
```

## Error Handling

### Classification Failure

If LLM classification fails, router defaults to "not-related":

```python
except Exception as e:
    error_payload = {
        "domain": "not-related",
        "reasoning": f"Classification failed: {str(e)}",
        "confidence": "low"
    }
    tree_data.environment.hidden_environment["domain_classification"] = error_payload
```

### Invalid Domain Returned

If LLM returns an invalid domain name:

```python
if domain not in valid_domains:
    logger.warning(f"Invalid domain '{domain}'. Defaulting to 'not-related'.")
    domain = "not-related"
```

## User-Facing Messages

The router yields status messages for the UI:

```python
# If specialized agent matched
yield Response(text="Routing to specialized agent: Immigration Law Expert...")

# If no match
yield Response(text="Processing your query with general tools...")
```

## Configuration

### Router Tool Definition

```python
class DomainRouter(Tool):
    def __init__(self, logger=None):
        super().__init__(
            name="domain_router",
            description=(
                "Evaluates if the query requires specialized domain knowledge. "
                "Routes to appropriate custom agents when needed."
            ),
            status="Evaluating query domain...",
            inputs={},
            end=False,  # Doesn't end the conversation
        )
```

### Registry Integration

The CustomAgentRegistry provides agent information to the router:

```python
# In tree initialization
custom_agents_info = {
    "names": registry.get_agent_names(),
    "descriptions": registry.get_agent_descriptions()
}
tree_data.environment.hidden_environment["custom_agents"] = custom_agents_info
```

## Implementation Details

### DSPy Signature

The router uses `ElysiaChainOfThought` for classification:

```python
classifier = ElysiaChainOfThought(
    DynamicPrompt,
    tree_data=tree_data,
    reasoning=False,
    impossible=False,
    environment=False,
    tasks_completed=False,
    message_update=False,
)
```

### Confidence Levels

| Level | Meaning |
|-------|---------|
| `high` | Clear match to agent domain |
| `medium` | Partial match, could be relevant |
| `low` | Uncertain classification |

## Debugging

### Enable Router Logging

```python
import logging
logging.getLogger("elysia.tools.domain.router").setLevel(logging.DEBUG)
```

### Log Output Examples

```text
Domain Router called!
User prompt preview (chars=150): What are the visa requirements...
Custom agents discovered: {'count': 2, 'names': ['Immigration Expert', 'Tax Advisor']}
Classification result: immigration expert
Reasoning: Query explicitly asks about visa requirements
Confidence: high
Stored classification in hidden_environment
```

## Troubleshooting

### Router Runs Multiple Times

**Cause**: Classification not being stored properly.

**Check**: Verify `hidden_environment` is preserved between iterations.

### Wrong Agent Selected

**Cause**: Agent descriptions not specific enough.

**Solution**: Improve agent descriptions to clearly define their domain.

### "not-related" for Specialized Query

**Cause**: Query wording doesn't match agent descriptions.

**Solutions**:
1. Add more keywords to agent descriptions
2. Use more specific domain terminology in queries
3. Check LLM classification reasoning in logs

### Custom Agents Not Appearing

**Cause**: Agents not loaded into registry.

**Check**:
1. Verify user has custom agents in Weaviate
2. Check registry load logs for errors
3. Ensure `hidden_environment["custom_agents"]` is populated

## Architecture

### File Location

```text
backend/elysia/tools/domain/
├── router.py              # DomainRouter Tool implementation
├── prompt_templates.py    # Dynamic prompt generation
└── objects.py            # DomainClassification result type
```

### Dependencies

```python
from elysia.objects import Response, Status, Tool
from elysia.tools.domain.objects import DomainClassification
from elysia.tools.domain.prompt_templates import create_domain_router_prompt
from elysia.tree.objects import TreeData
from elysia.util.elysia_chain_of_thought import ElysiaChainOfThought
```

## See Also

- [Agents Overview](index.md) - System and custom agents
- [Custom Agents](custom-agents.md) - Creating user-defined agents
- [Decision Tree](../../architecture/decision-tree.md) - How tools are selected
