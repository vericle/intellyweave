# AGENTS.md

## ⚠️ MANDATORY TASK COMPLETION CHECKLIST ⚠️

**🔴 BEFORE MARKING ANY TASK/SUBTASK AS COMPLETE:**

□ **AGENTS.md Updated**: Update this file if new features/commands/structure added

**❌ TASK IS NOT COMPLETE IF:**
- New code has unused function/methods/classes/types/objects/properties

## PERMANENT INSTRUCTIONS

**CRITICAL DEVELOPMENT RULES - NEVER OVERRIDE:**

1. **Always Check for Reusability**: Before implementing new functionality, ALWAYS search the codebase for existing similar functions or utilities that can be reused or extended. Never duplicate code - create shared utilities instead.

2. **AGENTS.md Updates**: Only update AGENTS.md for fundamental changes to development workflow, new architectural patterns, or structural changes that future developers need to know. Do NOT add recent updates, change logs, or temporary information - use git commits and PR descriptions for those.

3. **Never Make Assumptions - MANDATORY**: Before taking any action that involves external information, configuration, or user preferences, you MUST either:
   - **Ask the user** questions to clarify requirements
   - **Verify via documentation** using `gh` CLI (for GitHub repos) or WebFetch
   - **Query MCP servers** (like dot-ai) for authoritative answers

   This is **non-negotiable**. Do not guess, do not use "typical" defaults, do not assume.

4. **GitHub Operations**: For private repositories or any remote GitHub information, ALWAYS use `gh` CLI commands. Never guess repository URLs, user info, or remote state.

5. **Review Generated Content**: When using MCP servers or AI tools that generate templates/boilerplate:
   - **Critically review** all generated content before writing to files
   - **Adapt to reality** - remove aspirational language that doesn't match actual state
   - **Never blindly copy** template text (e.g., don't write "used worldwide" when there's 1 adopter)

6. **Verify Before Writing Config Files**: Before writing configuration files (renovate.json, workflow files, etc.):
   - Fetch reference examples from authoritative sources using `gh api`
   - Check official documentation
   - Ask user about specific preferences (schedules, assignees, exemptions)

**Note:** The following files are symlinks to this AGENTS.md:
- `AGENTS.md` - Claude Code
- `GEMINI.md` - Gemini CLI
- `.github/copilot-instructions.md` - GitHub Copilot

---

## ⚠️ MANDATORY: Python Virtual Environment

**BEFORE running ANY Python commands, tests, or scripts, you MUST activate the backend virtual environment:**

```bash
cd backend && source .venv/bin/activate
```

Or use the convenience script:

```bash
source backend/activate_venv.sh
```

**Never use system Python** (`/home/linuxbrew/.linuxbrew/bin/python3` or similar). Always use the virtual environment at `backend/.venv/bin/python`.

# IntellyWeave

**OSINT (Open-Source Intelligence) analysis platform** for intelligence analysts, historical researchers, and investigators.

Built on Weaviate's Elysia framework and inspired by the Spectre legal AI system, IntellyWeave specializes in intelligence analysis workflows with advanced entity extraction, geospatial visualization, and multi-agent reasoning.

**For project overview and purpose**: See [README.md](README.md)
**For technical implementation details**: See [backend/docs/backend-architecture.md](backend/docs/backend-architecture.md)

## Project Architecture

### Foundation & Inheritance

- **Base Framework**: Weaviate's Elysia (tracked via git subtrees)
  - Decision tree-based agent orchestration
  - Weaviate vector database integration
  - Query and aggregate tools

- **Inherited from Spectre** (legal AI system):
  - Document upload pipeline
  - Custom agent creation framework
  - Domain routing architecture
  - Courthouse debate orchestrator (adapted for intelligence analysis)
  - GPT-5 integration with reasoning controls

- **Unique to IntellyWeave** (OSINT-specific):
  - GLiNER entity extraction (7 types: persons, organizations, locations, events, dates, laws, cryptonyms)
  - Geospatial intelligence (Mapbox GL 3D mapping)
  - Network relationship analysis (vis-network graphs)

### Tech Stack

- **Backend**: Python 3.12 with FastAPI, Weaviate integration, DSPy for LLM orchestration, GLiNER entity extraction
- **Frontend**: Next.js 15 with TypeScript, React 18, Tailwind CSS, Radix UI components, Mapbox GL, vis-network
- **Focus**: OSINT intelligence analysis (NOT legal analysis - that's Spectre's domain)

## Current Capabilities

### Entity Extraction & Storage

- **GLiNER** multi-v2.1 model for zero-shot entity recognition
- **7 Entity Types**: persons, organizations, locations, events, dates, laws, cryptonyms
- Automatic extraction during document upload with deduplication
- Entities stored as Weaviate metadata arrays on document chunks

### Visualization

- **Geospatial**: Mapbox GL 3.16.0 with 3D controls for entity mapping
- **Network Graphs**: vis-network 10.0.2 with ForceAtlas2 physics for relationship analysis
- **Charts**: Bar, histogram, scatter, line charts via DSPy signatures

### Document Processing

- **Multi-format**: PDF (pypdf), TXT, Markdown support
- **Pipeline**: Parse → Extract entities → Chunk → Vectorize (OpenAI) → Store (Weaviate)
- **Collections**: `ELYSIA_UPLOADED_DOCUMENTS` and `ELYSIA_CHUNKED_*` with entity metadata
- **Inherited from Spectre**: Document upload pipeline, chunking system

### Agent Framework

- **Domain Router**: Query intent analysis and specialized agent selection (from Spectre)
- **Custom Agents**: User-defined agents with domain-specific knowledge bases (from Spectre)
- **Courthouse Debate**: Multi-agent system (defense, prosecution, judge) for complex analytical decisions
  - **Origin**: Created in Spectre for legal case analysis
  - **IntellyWeave Adaptation**: Intelligence assessment, not legal analysis
- **Tools**: Query, aggregate, retrieval with entity-aware filtering

### LLM Support

- **GPT-5 Integration**: Native Responses API client with reasoning effort and verbosity controls (from Spectre)
- **Multi-provider**: OpenAI, Anthropic, OpenRouter, Cohere, Mistral, local models via Ollama
- **Models**: Support for gpt-5, gpt-5-mini, gpt-5-nano, claude-sonnet-4-5, and others

## Build & Commands

### Setup (First Time)

```bash
# Full initial setup
scripts/setup.sh

# Manual backend setup
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .

# Manual frontend setup
cd frontend
pnpm install
```

### Development Commands

**Backend Development:**

```bash
cd backend
source .venv/bin/activate

# Start backend server (development mode with hot reload)
elysia start
# Default: http://localhost:8000, with --port and --host options available

# Start without reload
elysia start --reload=False

# Run backend tests (requires environment variables)

pytest tests/

# Run specific test file
pytest tests/requires_env/api/test_collections.py

# Run tests with coverage
pytest --cov=elysia tests/

# Deactivate virtual environment
deactivate
```

**Frontend Development:**

```bash
cd frontend

# Start development server (hot reload)
pnpm run dev
# Opens at http://localhost:3000

# Build frontend for production
pnpm run build
# Clean build
pnpm run build:clean

# Export static files
pnpm run export

# Full build and export to backend
pnpm run assemble

# Clean assemble
pnpm run assemble:clean

# Start production server
pnpm start

# Lint code
pnpm run lint

# Run tests (currently runs lint)
pnpm test
```

**Production Build:**

```bash
# Build everything from root
scripts/build.sh

# Then start backend
cd backend && source .venv/bin/activate && elysia start
# Access at http://localhost:8000
```

### Syncing with Upstream

```bash
# Backend updates from weaviate/elysia
git fetch upstream-backend main
git subtree pull --prefix=backend upstream-backend main --squash

# Frontend updates from weaviate/elysia-frontend
git fetch upstream-frontend main
git subtree pull --prefix=frontend upstream-frontend main --squash

# Rebuild after sync
scripts/build.sh
```

### Script Command Consistency

**Important**: When modifying pnpm   scripts in `frontend/package.json`, ensure all references are updated in:

- GitHub Actions workflows (if any)
- README.md and documentation
- `scripts/build.sh`
- `scripts/setup.sh`

**Note**: Always use the EXACT script names from package.json, not assumed names.

## Code Style

### Backend (Python)

**General Conventions:**

- Python 3.12 syntax and features
- Type hints for function parameters and return values
- Use `rich` library for console output with formatting
- Follow PEP 8 naming conventions

**Imports:**

```python
# Standard library first
import os
from dotenv import load_dotenv

# Third-party libraries
from rich import print
import click
import uvicorn

# Local imports last
from elysia.api.app import app
```

**Naming Conventions:**

- Functions and variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: prefix with single underscore `_private_method`

**Error Handling:**

- Use proper exception handling with specific exception types
- Provide meaningful error messages for debugging
- Use `rich` for formatted error output in CLI

**Dependencies:**

- Core: FastAPI, Uvicorn, Weaviate client, DSPy, LiteLLM
- Testing: pytest, pytest-asyncio, deepeval
- Documentation: mkdocs-material

### Frontend (TypeScript/React)

**General Conventions:**

- TypeScript strict mode enabled
- React 18 with functional components and hooks
- Next.js 15 App Router architecture
- Tailwind CSS for styling with custom configuration

**Imports:**

```typescript
// React and Next.js imports first
import { useContext } from "react";

// Path aliases using @/* for local imports
import { ToastContext } from "@/app/components/contexts/ToastContext";

// External libraries
import { clsx } from "clsx";
```

**Naming Conventions:**

- Components: `PascalCase` (e.g., `ToastContext`, `ApiErrorHandler`)
- Hooks: `camelCase` with `use` prefix (e.g., `useApiErrorHandler`)
- Functions and variables: `camelCase`
- Constants: `UPPER_SNAKE_CASE`
- Types and interfaces: `PascalCase`

**Component Structure:**

```typescript
// Type definitions first
interface Props {
  title: string;
  // ...
}

// Component definition
export const ComponentName = ({ title }: Props) => {
  // Hooks at top
  const { someValue } = useContext(SomeContext);

  // Event handlers
  const handleClick = () => {
    // ...
  };

  // Render
  return (
    // JSX
  );
};
```

**Error Handling:**

```typescript
try {
  const result = await apiCall();
  if (result.error) {
    handleApiError(result.error);
    return null;
  }
  return result;
} catch (error) {
  const errorMessage =
    error instanceof Error ? error.message : "An unexpected error occurred";
  handleApiError(errorMessage);
  return null;
}
```

**TypeScript Configuration:**

- Target: ES2017
- Strict mode enabled
- Path aliases: `@/*` maps to project root
- JSX: preserve (handled by Next.js)

**Formatting:**

- ESLint with next/core-web-vitals and next/typescript configs
- Prettier for consistent formatting (configured in devDependencies)
- 2-space indentation (inferred from tsconfig.json)

## Testing

### Backend Testing

**Framework**: pytest with pytest-asyncio for async tests

**Test File Patterns:**

- `tests/**/*.py`
- Tests organized in `tests/requires_env/` for tests needing environment setup
- `conftest.py` files for shared fixtures

**Running Tests:**

```bash
cd backend
source .venv/bin/activate

# Run all tests
pytest tests/

# Run specific test directory
pytest tests/requires_env/api/

# Run specific test file
pytest tests/requires_env/api/test_collections.py

# Run with coverage
pytest --cov=elysia tests/

# Run with verbose output
pytest -v tests/
```

**Test Categories:**

- `tests/requires_env/llm/` - LLM integration tests
- `tests/requires_env/api/` - API endpoint tests
- Tests require environment variables (Weaviate, API keys)

**Testing Conventions:**

- Use fixtures from `conftest.py` for common setup
- Use `deepeval` for LLM evaluation tests
- Mock external services when appropriate
- Test both success and error cases

### Frontend Testing

**Framework**: Currently basic (uses lint as test command)

**Running Tests:**

```bash
cd frontend

# Run tests (currently runs lint)
pnpm   test

# Run lint explicitly
pnpm   run lint
```

### Testing Philosophy

**When tests fail, fix the code, not the test.**

Key principles:

- **Tests should be meaningful** - Avoid tests that always pass regardless of behavior
- **Test actual functionality** - Call the functions being tested, don't just check side effects
- **Failing tests are valuable** - They reveal bugs or missing features
- **Fix the root cause** - When a test fails, fix the underlying issue, don't hide the test
- **Test edge cases** - Tests that reveal limitations help improve the code
- **Document test purpose** - Each test should clearly indicate what it validates

## Security

### Authentication & Authorization

- Backend uses API key-based authentication
- User registration and login with bcrypt password hashing
- Support for multiple API key providers (OpenAI, Anthropic, etc.)

### API Keys & Secrets

**Backend Environment Variables** (`backend/.env`):

```bash
# Weaviate Configuration
WCD_URL=your-weaviate-cloud-url
WCD_API_KEY=your-weaviate-api-key

# Or for local Weaviate
WEAVIATE_IS_LOCAL=True
LOCAL_WEAVIATE_PORT=8080
LOCAL_WEAVIATE_GRPC_PORT=50051

# Or for custom Weaviate
WEAVIATE_IS_CUSTOM=True
CUSTOM_HTTP_HOST=your.weaviate.host
CUSTOM_HTTP_PORT=443
CUSTOM_HTTP_SECURE=True

# LLM Provider API Keys
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
OPENROUTER_API_KEY=your-openrouter-key
# Plus many others: Cohere, Mistral, AWS, Azure, etc.

# Model Configuration
BASE_MODEL=gemini-2.0-flash-001
COMPLEX_MODEL=gemini-2.0-flash-001
BASE_PROVIDER=openrouter/google
COMPLEX_PROVIDER=openrouter/google
```

**Security Best Practices:**

- Never commit `.env` files
- Use `.env.example` as template
- Rotate API keys regularly
- Use environment-specific configurations
- Validate all API inputs
- Use HTTPS in production
- Implement rate limiting for API endpoints

### Data Protection

- Secure handling of user queries and responses
- Vector database encryption (Weaviate feature)
- Secure WebSocket connections for real-time features

## Directory Structure & File Organization

### Repository Structure

```bash
intellyweave/
├── backend/              # Python FastAPI backend
│   ├── elysia/          # Main package
│   │   ├── api/         # API endpoints and CLI
│   │   ├── llm/         # LLM integration
│   │   └── ...
│   ├── tests/           # Backend tests
│   ├── docs/            # Backend documentation
│   ├── .env.example     # Environment template
│   └── pyproject.toml   # Python dependencies
├── frontend/            # Next.js frontend
│   ├── app/            # Next.js App Router
│   ├── components/     # React components
│   ├── hooks/          # Custom React hooks
│   ├── lib/            # Utility libraries
│   ├── public/         # Static assets
│   └── package.json    # Node dependencies
├── scripts/            # Build and setup scripts
│   ├── setup.sh        # Initial setup
│   └── build.sh        # Production build
├── docs/               # Project documentation
├── temp/               # Temporary files (add to .gitignore)
└── .claude/            # Claude Code configuration
    └── agents/         # Specialized AI agents
```

### Temporary Files & Debugging

All temporary files, debugging scripts, and test artifacts should be organized in a `/temp` folder:

**Temporary File Organization:**

- **Debug scripts**: `temp/debug-*.js`, `temp/analyze-*.py`
- **Test artifacts**: `temp/test-results/`, `temp/coverage/`
- **Generated files**: `temp/generated/`, `temp/build-artifacts/`
- **Logs**: `temp/logs/debug.log`, `temp/logs/error.log`

**Guidelines:**

- Never commit files from `/temp` directory
- Use `/temp` for all debugging and analysis scripts created during development
- Clean up `/temp` directory regularly or use automated cleanup
- Include `/temp/` in `.gitignore` to prevent accidental commits

### Example `.gitignore` patterns

```bash
# Temporary files and debugging
/temp/
temp/
**/temp/
debug-*.js
debug-*.py
test-*.py
analyze-*.sh
*-debug.*
*.debug

# Python
__pycache__/
*.py[cod]
.venv/
*.egg-info/

# Node
node_modules/
.next/
out/

# Environment
.env
.env.local



```

### Claude Code Settings (.claude Directory)

The `.claude` directory contains Claude Code configuration files with specific version control rules:

**Important Notes:**
- Hook scripts in `.claude/hooks/` should be executable (`chmod +x`)

## Configuration

### Environment Setup

**Prerequisites:**

- **Python**: 3.12 (required)
- **Node.js**: 18 or higher (required)
- **Weaviate**: Running instance (local, cloud, or custom)

### Backend Configuration

**Environment Variables** (`backend/.env`):

See Security section for complete list of available environment variables.

**Python Dependencies**:

Managed via `pyproject.toml` with these key packages:

- fastapi[standard] - Web framework
- weaviate-client - Vector database client
- dspy-ai - LLM orchestration
- litellm - Multi-provider LLM interface
- uvicorn - ASGI server
- pytest, deepeval - Testing

**Installation:**

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e .              # Development install
pip install -e ".[dev]"       # With dev dependencies
```

### Frontend Configuration

**TypeScript Configuration** (`frontend/tsconfig.json`):

- Target: ES2017
- Strict mode enabled
- Path aliases: `@/*` maps to root

**Node Dependencies**:

Key packages from `frontend/package.json`:

- next@15 - Framework
- react@18 - UI library
- typescript@5 - Type safety
- tailwindcss - Styling
- @radix-ui/* - UI components
- framer-motion - Animations

**Installation:**

```bash
cd frontend
pnpm   install
```

### Development Environment

**Backend + Frontend Development (recommended):**

```bash
# Terminal 1: Backend
cd backend
source .venv/bin/activate
elysia start

# Terminal 2: Frontend dev server
cd frontend
pnpm   run dev
# Access at http://localhost:3000
```

**Backend Only (production-like):**

```bash
scripts/build.sh
cd backend
source .venv/bin/activate
elysia start
# Access at http://localhost:8000 (serves built frontend)
```

## Agent Delegation & Tool Execution

### ⚠️ MANDATORY: Always Delegate to Specialists & Execute in Parallel

**When specialized agents are available, you MUST use them instead of attempting tasks yourself.**

**When performing multiple operations, send all tool calls (including Task calls for agent delegation) in a single message to execute them concurrently for optimal performance.**

### Available Specialized Agents

This project has the following Claude Code agents configured in `.claude/agents/`:

1. **git-expert** (`.claude/agents/git/git-expert.md`)
   - Git workflows, merge conflicts, branching strategies
   - Repository recovery and history management
   - Especially useful for git subtree operations

2. **nestjs-expert** (`.claude/agents/nestjs-expert.md`)
   - NestJS module architecture and dependency injection
   - Note: Backend uses FastAPI, not NestJS - use for reference only

3. **framework-nextjs-expert** (`.claude/agents/framework/framework-nextjs-expert.md`)
   - Next.js App Router, Server Components
   - Performance optimization and full-stack patterns
   - **USE THIS for frontend architecture questions**

4. **code-search** (`.claude/agents/code-search.md`)
   - Specialized codebase searching
   - Finding files, functions, and patterns efficiently

5. **documentation-expert** (`.claude/agents/documentation/documentation-expert.md`)
   - Documentation structure and quality
   - Information architecture and content organization

6. **e2e-playwright-expert** (`.claude/agents/e2e/e2e-playwright-expert.md`)
   - End-to-end testing with Playwright
   - Test automation and CI/CD integration

### Why Agent Delegation Matters

- Specialists have deeper, more focused knowledge
- They're aware of edge cases and subtle bugs
- They follow established patterns and best practices
- They can provide more comprehensive solutions

### Key Principles

- **Agent Delegation**: Always check if a specialized agent exists for your task domain
- **Complex Problems**: Delegate to domain experts, use diagnostic agents when scope is unclear
- **Multiple Agents**: Send multiple Task tool calls in a single message to delegate to specialists in parallel
- **DEFAULT TO PARALLEL**: Unless you have a specific reason why operations MUST be sequential (output of A required for input of B), always execute multiple tools simultaneously
- **Plan Upfront**: Think "What information do I need to fully answer this question?" Then execute all searches together

### Critical: Always Use Parallel Tool Calls

**Err on the side of maximizing parallel tool calls rather than running sequentially.**

**IMPORTANT: Send all tool calls in a single message to execute them in parallel.**

**These cases MUST use parallel tool calls:**

- Searching for different patterns (imports, usage, definitions)
- Multiple grep searches with different regex patterns
- Reading multiple files or searching different directories
- Combining Glob with Grep for comprehensive results
- Searching for multiple independent concepts
- Agent delegations with multiple Task calls to different specialists

**Sequential calls ONLY when:**

You genuinely REQUIRE the output of one tool to determine the usage of the next tool.

**Planning Approach:**

1. Before making tool calls, think: "What information do I need to fully answer this question?"
2. Send all tool calls in a single message to execute them in parallel
3. Execute all those searches together rather than waiting for each result
4. Most of the time, parallel tool calls can be used rather than sequential

**Performance Impact:** Parallel tool execution is 3-5x faster than sequential calls, significantly improving user experience.

**Remember:** This is not just an optimization—it's the expected behavior. Both delegation and parallel execution are requirements, not suggestions.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Creating feature branches
- Commit message conventions (feat:, fix:, docs:, etc.)
- Testing requirements
- Documentation guidelines
- Contributing changes back to upstream Weaviate repositories

### Commit Message Convention

```bash
feat: add custom authentication handler
fix: resolve WebSocket connection timeout
docs: update setup instructions
refactor: reorganize API endpoints
test: add integration tests for collections API
chore: update dependencies
```

### Working with Upstream

This repository tracks upstream changes via git subtrees:

- Backend: <https://github.com/weaviate/elysia>
- Frontend: <https://github.com/weaviate/elysia-frontend>

Always document custom modifications and consider contributing valuable changes back upstream.

## Common Issues

| Issue | Solution |
|-------|----------|
| Port 8000 in use | `lsof -i :8000` then `kill -9 <PID>` |
| Build fails | Check Python 3.12 and Node 18+ |
| Frontend can't connect | Ensure backend runs on port 8000 |
| Merge conflicts during sync | See [docs/syncing.md](docs/syncing.md) |
| Python venv issues | Delete `.venv` and re-run `scripts/setup.sh` |
| pnpm   install fails | Delete `node_modules` and `package-lock.json`, re-run |
| Tests fail with missing env | Copy `.env.example` to `.env` and configure API keys |

## Additional Resources

- **Backend README**: [backend/README.md](backend/README.md)
- **Frontend README**: [frontend/README.md](frontend/README.md)
- **Elysia Documentation**: <https://weaviate.github.io/elysia/>
- **Weaviate Documentation**: <https://weaviate.io/developers/weaviate>
