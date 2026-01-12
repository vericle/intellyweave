# IntellyWeave CLI

<p align="center">
    <img src="images/ai-powered-cli.jpg" alt="IntellyWeave CLI - Interactive Shell" width="700">
</p>

**Operations backbone for IntellyWeave—manage Weaviate databases, migrate data, configure archives, and query with AI.**

---

## What It Does

IntellyWeave CLI provides direct command-line access to the IntellyWeave platform's data layer. It enables database administration, backup/restore operations, archive source configuration, and an AI-powered interactive shell for natural language queries.

## Use When

- Managing Weaviate collections and objects without the web UI
- Backing up or migrating data between environments
- Adding new archive sources for the [Quartermaster agent](../guides/archive-research/configuration.md)
- Debugging data issues or exploring collections programmatically
- Automating operations in CI/CD pipelines

---

## Key Capabilities

### 1. Weaviate Database Management

Direct access to all Weaviate operations from the command line.

```bash
# List all collections with statistics
intellyweave weaviate collections --verbose

# Hybrid search across document chunks
intellyweave weaviate search ELYSIA_CHUNKED "Vatican escape routes"

# Check connection health
intellyweave weaviate status
```

| Command | Description |
|---------|-------------|
| `weaviate status` | Check connection health |
| `weaviate collections` | List all collections |
| `weaviate stats` | Show database statistics |
| `weaviate search` | Hybrid keyword + vector search |
| `weaviate objects` | Browse collection objects |
| `weaviate delete` | Delete collections (requires `--live`) |

### 2. Data Import/Export

Backup, restore, and migrate Weaviate data with JSON files.

```bash
# Export all collections to backup directory
intellyweave data export --output-dir ./backup-2026-01-06

# Preview import (dry-run by default)
intellyweave data import --input-dir ./backup

# Execute import with --live flag
intellyweave --live data import --input-dir ./backup
```

**Mutation Safety**: All data-modifying operations require explicit `--live` flag to prevent accidental data loss.

### 3. Interactive AI Shell

Natural language queries powered by Claude. Ask questions, get answers.

```bash
intellyweave shell
```

```
IntellyWeave Interactive Shell
Type :help or / for features. Press <TAB> for suggestions.

Loading 1 MCP server(s).
Loaded MCP servers: perplexity-mcp
4 tools total

intellyweave> How many documents are in Weaviate?
Checking collection statistics...
You have 1,234 documents across 5 collections.
```

| Feature | Description |
|---------|-------------|
| Natural Language | Ask questions in plain English |
| Quick Commands | `/collections`, `/stats`, `/config` |
| MCP Integration | Connect to AI tool servers |
| Mode Toggles | `/live`, `/json`, `/verbose` |

### 4. Archive Configuration

Configure archive sources for the [Quartermaster agent](../guides/archive-research/index.md).

```bash
# Research and add a new archive source
intellyweave archive config add https://bundesarchiv.de

# Output: Researching archive via Perplexity...
# Output: Generated YAML appended to ./data/archive_domains_update.yaml
```

This generates properly formatted YAML for the platform's [`archive_domains.yaml`](../guides/archive-research/configuration.md) configuration—including access levels, digitization status, and authentication requirements.

---

## Installation

```bash
# Clone the repository
git clone https://github.com/vericle/intellyweave-cli.git
cd intellyweave-cli

# Install dependencies
npm install

# Run CLI in development mode
npm run dev -- --help
```

## Configuration

Create `.env` in your project root:

```bash
# Weaviate Connection
WEAVIATE_URL=http://localhost:8080

# Or for Weaviate Cloud
# WCD_URL=https://your-cluster.weaviate.network
# WCD_API_KEY=your-api-key

# AI Agent (optional, for interactive shell)
ANTHROPIC_API_KEY=sk-ant-...
```

---

## Architecture Relationship

```
┌─────────────────────────────────────────────────────────────┐
│              IntellyWeave Platform (Web UI)                 │
│  Entity Extraction • Geospatial Maps • Network Analysis     │
│  Archive Research • Courthouse Debate • Intelligence Agent  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Weaviate Vector DB                       │
│  ELYSIA_UPLOADED_DOCUMENTS • ELYSIA_CHUNKED_* • Metadata    │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────┐
│              IntellyWeave CLI (This Tool)                   │
│  Database Ops • Data Migration • Archive Config • AI Shell  │
└─────────────────────────────────────────────────────────────┘
```

---

## Technical Stack

| Component | Technology |
|-----------|------------|
| Language | TypeScript 5.7+ (ESM) |
| CLI Framework | Commander.js 12.x |
| Database Client | weaviate-client 3.x |
| AI Integration | Vercel AI SDK + Anthropic Claude |
| MCP Protocol | @modelcontextprotocol/sdk 1.x |

---

## See Also

- **[IntellyWeave CLI Repository](https://github.com/vericle/intellyweave-cli)** — Full documentation and source code
- [Archive Research Configuration](../guides/archive-research/configuration.md) — Archive domains YAML format
- [Document Processing Pipeline](../guides/document-processing/index.md) — How documents flow into Weaviate
- [Environment Variables](../reference/environment-variables.md) — Platform configuration options
