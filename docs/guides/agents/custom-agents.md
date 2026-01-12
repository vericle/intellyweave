# Custom Agents

**User-defined agents with dedicated knowledge bases that the Domain Router can automatically select.**

## What It Does

Custom Agents allow users to:

1. Upload documents to create a dedicated knowledge base
2. Define agent name, description, and system prompt
3. Have IntellyWeave automatically route relevant queries to the agent
4. Get responses grounded in the agent's knowledge base

## Use When

- You have specialized documents for a specific domain
- You want automatic routing for domain-specific queries
- You need consistent, document-grounded responses
- You want to create expert assistants for specific topics

## Creating Custom Agents

### Via the UI

1. Navigate to **Agents & Remote Tools** page
2. Click **Create Agent** button
3. Upload a document (PDF, TXT, DOCX, MD)
4. Fill in agent details:
   - **Agent Name**: Human-readable name (used for routing)
   - **Agent Description**: What the agent specializes in (used for classification)
   - **System Prompt**: Instructions defining agent behavior

### Agent Configuration

| Field | Purpose | Example |
|-------|---------|---------|
| **Name** | Identifies agent in router and UI | "Immigration Law Expert" |
| **Description** | Helps router classify queries | "Specializes in visa requirements and immigration procedures" |
| **System Prompt** | Defines agent behavior | "You are an expert in immigration law. Always cite specific sections..." |
| **Document** | Knowledge base source | Uploaded PDF or text file |

### System Prompt Best Practices

```text
You are a specialized expert in [domain]. Your knowledge is based on the
uploaded document. When answering questions:

- Focus on [specific topics]
- Cite specific sections from the document
- Explain complex concepts clearly
- Recommend professional consultation when needed
- Acknowledge when information is outside your knowledge base
```

## UI Components

### Agent Library

**Location**: `frontend/app/components/agents/AgentLibrary.tsx`

The main agent management interface:

| Feature | Description |
|---------|-------------|
| **Search** | Filter agents by name or description |
| **Stats** | Shows count of custom vs remote agents |
| **Grid View** | Cards for each agent |
| **Create Button** | Opens document upload dialog |
| **Refresh** | Reloads agent list from Weaviate |

### Agent Card

**Location**: `frontend/app/components/agents/AgentCard.tsx`

Individual agent display with:

| Element | Description |
|---------|-------------|
| **Icon** | Bot icon for custom, Cloud icon for remote |
| **Badge** | "CUSTOM AGENT" or "REMOTE AGENT" |
| **Description** | Agent's specialization |
| **Capabilities** | Tags for agent features |
| **Actions** | Edit/Delete buttons (custom only) |
| **Metadata** | Document ID, creation date |

### Visual Styling

| Agent Type | Border Color | Background |
|------------|--------------|------------|
| **Custom** | Accent color | Accent gradient |
| **Remote** | Blue | Blue gradient |

### Agent Edit Dialog

**Location**: `frontend/app/components/agents/AgentEditDialog.tsx`

Edit agent properties:
- Agent name
- Description
- System prompt (multi-line textarea)

## Remote Agents

Remote agents are managed by IntellyWeave/Weaviate Cloud:

| Property | Value |
|----------|-------|
| **Editable** | No (read-only) |
| **Deletable** | No |
| **Source** | `weaviate_remote` |
| **ID Prefix** | `remote:` |
| **Badge** | "Managed by IntellyWeave" |

Remote agents are included for transparency—users can see what tools IntellyWeave may invoke automatically.

## Backend Architecture

### Storage

Custom agents are stored in Weaviate:

```python
agent_metadata = {
    "agent_id": "uuid-string",
    "agent_name": "Immigration Law Expert",
    "agent_description": "Specializes in visa requirements",
    "system_prompt": "You are an expert...",
    "document_id": "uuid-of-knowledge-base",
    "user_id": "owner-user-id",
    "created_date": "2024-01-15T10:30:00Z"
}
```

### Loading Flow

```text
Session Start
    │
    ▼
CustomAgentRegistry.load_custom_agents(user_id)
    │
    ├── Query Weaviate for user's agents
    ├── Instantiate via CustomAgentFactory
    └── Add to registry for routing
```

### Factory Pattern

**File**: `backend/elysia/tools/domain/custom_agent_factory.py`

Creates dynamic Tool subclasses:

```python
class DynamicCustomAgent(Tool):
    def __init__(self):
        super().__init__(
            name=agent_name,           # From metadata
            description=agent_description,
            status=f"Consulting {agent_name}...",
            end=True                   # Ends conversation turn
        )

    async def __call__(self, tree_data, ...):
        # 1. Query knowledge base (hybrid search)
        # 2. Retrieve top 5 chunks
        # 3. Generate response using system prompt
        # 4. Return with citations
```

### Query Execution

When a custom agent is selected:

1. **Hybrid search** on agent's document chunks
2. **Filter by document_id** via Weaviate reference
3. **Format chunks** for LLM context
4. **Generate response** using system prompt + retrieved docs
5. **Return TextWithCitations** linking to source chunks

## Domain Router Integration

### How Routing Works

1. **Router loads** custom agent names and descriptions
2. **LLM classifies** query into one domain
3. **Classification stored** in `hidden_environment`
4. **Custom agent checks** `is_tool_available()`
5. **Agent processes** if classification matches

### Availability Check

```python
async def is_tool_available(self, tree_data, ...):
    classification = tree_data.environment.hidden_environment.get(
        "domain_classification", {}
    )
    classified_domain = classification.get("domain", "")

    return (
        classified_domain == self.agent_name
        or classified_domain == f"custom_agent_{self.agent_id}"
        or classified_domain == self.agent_id
    )
```

## API Endpoints

### List Agents

```bash
GET /agents/{user_id}/list
```

Returns all agents for a user (custom + remote).

### Create Agent

```bash
POST /documents/{user_id}/upload?create_agent=true
Content-Type: multipart/form-data

{
  "file": <document>,
  "agent_name": "Immigration Expert",
  "agent_description": "Specializes in visa questions",
  "system_prompt": "You are an expert..."
}
```

### Update Agent

```bash
PATCH /agents/{user_id}/{agent_id}
Content-Type: application/json

{
  "agent_name": "Updated Name",
  "agent_description": "Updated description",
  "system_prompt": "Updated prompt..."
}
```

### Delete Agent

```bash
DELETE /agents/{user_id}/{agent_id}
```

Deletes agent metadata (document remains).

## Troubleshooting

### Agent Not Appearing in Library

**Cause**: Agent metadata not saved or user_id mismatch.

**Solution**:
- Check upload response for success
- Verify user_id in agent metadata matches current user

### Router Not Selecting Agent

**Cause**: Agent description doesn't match query patterns.

**Solution**:
- Make description more specific
- Include key domain terms
- Test with explicit domain-related queries

### Empty Responses

**Cause**: Document not properly chunked or wrong document_id.

**Solution**:
- Verify document upload succeeded
- Check document_id in agent metadata
- Confirm chunks exist in `ELYSIA_CHUNKED_*` collection

### Slow Response Times

**Cause**: Large knowledge base or complex queries.

**Solution**:
- Limit document size
- Use more specific queries
- Check Weaviate performance

## See Also

- [Agents Overview](index.md) - System agents and routing
- [Domain Router](domain-router.md) - Classification details
- [Document Upload](../../getting-started/first-query.md) - Upload process
