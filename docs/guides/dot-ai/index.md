# dot-ai MCP Server: Complete Guide

## Overview

The **dot-ai MCP** (DevOps AI Toolkit) is an AI-powered automation framework that integrates with Claude Code via Model Context Protocol. For IntellyWeave, we leverage it primarily for:

1. **Repository Governance** - Automated generation of 25+ standardized files (already done)
2. **PRD Workflow** - Documentation-first feature development via shared prompts
3. **Dockerfile Generation** - Production-ready container configurations

**What we DON'T use** (Kubernetes-specific features):

- `recommend` - K8s deployment recommendations
- `operate` - K8s Day 2 operations
- `remediate` - K8s issue troubleshooting
- `manageOrgData` - K8s patterns/policies

---

## Current Setup Status

### System Health Check

```text
Tool: mcp__dot-ai__version
```

**Current Configuration (v0.157.0):**

| Component | Status | Details |
|-----------|--------|---------|
| Vector DB (Qdrant) | ✅ Connected | `localhost:6333` |
| Embedding | ✅ Ready | OpenAI `text-embedding-3-small` |
| AI Provider | ✅ Connected | Anthropic Claude |

### What's Already Implemented

IntellyWeave has completed the `projectSetup` workflow. All governance files are in place:

**Root Level:**

- `LICENSE` (BSD 3-Clause)
- `CODE_OF_CONDUCT.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `SUPPORT.md`
- `ADOPTERS.md`

**GitHub Configuration (`.github/`):**

- `CODEOWNERS`
- `PULL_REQUEST_TEMPLATE.md`
- `labeler.yml`, `release.yml`
- `ISSUE_TEMPLATE/` - bug_report.yml, feature_request.yml, config.yml
- `workflows/` - labeler.yml, scorecard.yml, stale.yml

**Documentation (`docs/`):**

- `GOVERNANCE.md`
- `MAINTAINERS.md`
- `ROADMAP.md`

---

## ⚠️ GOLDEN RULES - NEVER SKIP ⚠️

1. **Never assume answers** - Always ask user or verify with `gh` CLI
2. **Review generated content** - MCP templates need human judgment
3. **Match reality** - Don't write boilerplate that doesn't reflect actual state
4. **Verify config files** - Fetch reference examples before writing

---

## Part 1: Shared Prompts (PRD Workflow)

The dot-ai MCP serves shared prompts as native slash commands. These enable a **documentation-first development approach** where features are planned in PRD files before implementation.

### Available Prompts

| Command | Purpose |
|---------|---------|
| `/dot-ai:prd-create` | Create a new PRD (GitHub issue + `prds/` file) |
| `/dot-ai:prds-get` | List all open PRDs with analysis |
| `/dot-ai:prd-start` | Begin implementation (creates feature branch) |
| `/dot-ai:prd-next` | Identify highest-priority next task |
| `/dot-ai:prd-update-progress` | Update PRD based on git commits |
| `/dot-ai:prd-update-decisions` | Capture design decisions from conversation |
| `/dot-ai:prd-done` | Complete PRD (create PR, merge, close issue) |
| `/dot-ai:prd-close` | Close PRD without PR (superseded/implemented elsewhere) |
| `/dot-ai:generate-dockerfile` | Generate production-ready Dockerfile |

### PRD Workflow Overview

```text
prd-create → prd-start → [prd-next → implement → prd-update-progress]* → prd-done
```

### Setting Up PRD Workflow

**1. Create the PRDs directory:**

```bash
mkdir -p prds
```

**2. Start a new feature:**

```bash
/dot-ai:prd-create
```

This will:

- Ask about your feature concept
- Create a GitHub issue with `PRD` label
- Create `prds/[issue-id]-[feature-name].md`
- Link the issue to the PRD file

**3. PRD File Structure:**

```markdown
## PRD: [Feature Name]

**Problem**: What problem does this solve?
**Solution**: How will we solve it?

### Milestones (5-10 major items)
- [ ] Core functionality implemented
- [ ] Documentation complete
- [ ] Integration working
- [ ] Tests passing
- [ ] Ready for release

### Work Log
| Date | Changes |
|------|---------|
| YYYY-MM-DD | Initial PRD created |
```

### PRD Best Practices (from devopstoolkit.live)

**Good Milestones:**

- Core functionality implemented and working
- Documentation complete and tested
- Integration with existing systems working
- Feature ready for user testing

**Avoid Micro-Tasks:**

- ❌ Update README.md file
- ❌ Write test for function X
- ❌ Fix typo in documentation

**Milestone Characteristics:**

- **Meaningful**: Represents significant progress
- **Testable**: Clear success criteria
- **User-focused**: Relates to user value
- **Manageable**: Reasonable timeframe

### Prompts as Production Code

From the [DevOps Toolkit blog](https://devopstoolkit.live/ai/stop-wasting-time-turn-ai-prompts-into-production-code):

> "They're not just instructions. They're your team's collective knowledge, encoded in a way that AI can execute."

Key principles:

- **Version control prompts** like code
- **Distribute via MCP** instead of copy-paste
- **Iterate and refine** through multiple versions

---

## Part 2: Documentation Best Practices

This section captures insights from [devopstoolkit.live](https://devopstoolkit.live) and the [devopstoolkit-live](https://github.com/vfarcic/devopstoolkit-live) repository about organizing and publishing documentation.

### Why NOT GitHub Wiki

| Aspect | GitHub Wiki | Docs in Repo |
|--------|-------------|--------------|
| **Version Control** | Separate repo, harder to track | ✅ Same repo, full history |
| **PR Reviews** | Not possible | ✅ Review docs with code |
| **Search** | Limited | ✅ Works with IDE/grep |
| **Cross-linking** | Fragile | ✅ Relative paths work |
| **CI/CD Integration** | Difficult | ✅ Can validate/build docs |
| **Contribution Flow** | Separate process | ✅ Same as code PRs |
| **Forks/Clones** | Wiki doesn't clone | ✅ Docs come with code |

**Recommendation:** Keep documentation in `docs/` directory within the repository.

### Topic-Based Organization Pattern

The [devopstoolkit-live](https://github.com/vfarcic/devopstoolkit-live) blog (Hugo-based) uses topic-based organization:

```text
content/
├── _index.md              # Landing page
├── ai/                    # AI & automation articles
│   └── [article-name]/
│       ├── _index.md      # Article content
│       └── images/        # Article-specific images
├── kubernetes/            # K8s-specific content
├── development/           # Development tools
├── infrastructure-as-code/
├── observability/
├── security/
└── [topic]/
```

**Key Insight:** Each article is in its **own directory** with `_index.md`, allowing co-location of images and related assets.

### Recommended Documentation Structure for IntellyWeave

```text
docs/
├── CLAUDE.md                    # AI assistant instructions for docs
├── GOVERNANCE.md                # Decision-making process
├── MAINTAINERS.md               # Current maintainers
├── ROADMAP.md                   # Project direction
│
├── getting-started/             # Onboarding guides
│   ├── index.md                 # Quick start
│   ├── installation.md
│   └── first-query.md
│
├── guides/                      # Feature-specific guides
│   ├── entity-extraction/       # Each feature gets its own directory
│   │   ├── index.md
│   │   ├── gliner-setup.md
│   │   └── images/
│   ├── geospatial-mapping/
│   │   ├── index.md
│   │   ├── mapbox-configuration.md
│   │   └── images/
│   ├── network-analysis/
│   │   └── index.md
│   └── multi-agent-debate/
│       ├── index.md
│       └── courthouse-workflow.md
│
├── architecture/                # Technical deep-dives
│   ├── backend-architecture.md
│   ├── frontend-architecture.md
│   └── data-flow.md
│
├── reference/                   # API and configuration reference
│   ├── api-endpoints.md
│   ├── environment-variables.md
│   └── cli-commands.md
│
└── contributing/                # Contributor guides
    ├── development-setup.md
    ├── testing.md
    └── upstream-syncing.md
```

### Documentation Organization Principles

#### 1. Each guide in its own directory

Co-locate related assets (images, code samples, data files) with the documentation:

```text
guides/entity-extraction/
├── index.md              # Main content
├── advanced-usage.md     # Additional pages
├── images/
│   ├── entity-types.png
│   └── extraction-flow.png
└── examples/
    └── sample-document.txt
```

#### 2. Topic-based grouping

Group by domain/feature, not by file type:

```text
✅ Good: guides/entity-extraction/images/
❌ Bad:  images/entity-extraction/
```

#### 3. README.md coordination

Keep root `README.md` in sync with detailed docs:

- Major feature additions should update both
- Cross-reference detailed guides from README
- Avoid duplicating content - link instead

#### 4. Validate before documenting

From `docs/CLAUDE.md` validation workflow:

- **Execute every command** in a test environment before documenting
- **Include actual output** where relevant
- **Test configuration files** to ensure they work
- **Use real examples** from testing, not theoretical ones

### Content Quality Standards

From [devopstoolkit.live](https://devopstoolkit.live) patterns:

**Every guide should include:**

| Section | Purpose |
|---------|---------|
| **What it does** | Clear, concise description |
| **Use when** | Specific scenarios/triggers |
| **Prerequisites** | What's needed before starting |
| **Step-by-step** | Numbered, actionable instructions |
| **Examples** | Real, tested code/commands |
| **Troubleshooting** | Common issues and solutions |
| **See also** | Related documentation links |

**Formatting conventions:**

- Use tables for comparisons (Pros/Cons/Best For)
- Use status indicators: ✅ ❌ ⚠️ 🎯 🚀
- Use code blocks with syntax highlighting (`bash`, `yaml`, `json`, `python`)
- Include "🎯 Recommended" markers for preferred options

### Knowledge Organization Insights

From [Teaching AI Company Policies](https://devopstoolkit.live/ai/teaching-ai-your-company-policies-vector-search-enforcement):

> "Policies are buried in internal documents and wiki pages that nobody reads. They're hidden in existing code as comments or conventions. Most critically, policies are locked in people's heads."

**Solution patterns:**

1. **Extract implicit knowledge** into explicit documentation
2. **Store with semantic meaning** (IntellyWeave already uses Weaviate!)
3. **Make discoverable** via search, not just navigation
4. **Keep close to code** - documentation that lives with code stays current

### Publishing Options

| Option | Tool | Best For | IntellyWeave Status |
|--------|------|----------|---------------------|
| **In-repo docs** | Markdown in `docs/` | Technical docs, architecture | ✅ Current approach |
| **Static site** | MkDocs Material | Public-facing guides | Available (in backend deps) |
| **GitHub Pages** | Jekyll/Hugo | Published documentation | Future option |
| **API reference** | OpenAPI/Swagger | REST API docs | Future option |

**MkDocs Material** is already in backend dependencies - consider using it for published documentation.

### Demos & Examples Organization

IntellyWeave includes curated demo datasets and multimedia content to showcase platform capabilities. These require special organization to maintain clarity between **source data** (for ingestion) and **documentation** (for users).

#### The `examples/` Directory Pattern

Demo datasets live in `examples/` at the repository root, separate from `docs/`:

```text
examples/
├── README.md                    # Master documentation for the demo
├── cleaned/                     # Source documents ready for ingestion
│   ├── [category]/              # Organized by document type
│   │   └── [document]_[score].txt   # Scored by relevance (10-100)
│   └── ...
└── multimedia/                  # Generated demo content
    ├── audio/                   # Podcasts + transcriptions
    ├── video/                   # Videos + transcriptions
    ├── pdf/                     # Presentation slides
    ├── images/                  # Screenshots, diagrams
    └── [interactive-tools]/     # Tool-specific exports
```

**Why separate from `docs/`?**

| Location | Purpose |
|----------|---------|
| `examples/` | Data files that IntellyWeave ingests (`.txt`, `.mp3`, `.mp4`, `.pdf`) |
| `docs/demos/` | User-facing documentation *about* the demos |

#### Demo Documentation Structure

Following the topic-based organization principle, each demo gets its own directory in `docs/demos/`:

```text
docs/
├── ... (existing docs)
└── demos/                           # Demo & Tutorial Section
    ├── index.md                     # Demo catalog and overview
    │
    └── [demo-name]/                 # One directory per demo
        ├── index.md                 # Demo overview and purpose
        ├── dataset.md               # Document inventory, scoring methodology
        ├── walkthrough.md           # Step-by-step usage guide
        │
        └── multimedia/              # Documentation about multimedia assets
            ├── index.md             # Multimedia catalog
            └── [asset-type].md      # Summaries linking to examples/multimedia/
```

#### Key Principles

1. **Source data stays in `examples/`** — These are ingested by IntellyWeave, not served as docs
2. **Documentation lives in `docs/demos/`** — User-facing guides, not raw data
3. **Link, don't duplicate** — Multimedia files stay in `examples/multimedia/`, docs reference them
4. **Transcripts become summaries** — Audio/video transcripts are summarized in markdown, not copied verbatim
5. **Each demo is self-contained** — All related docs co-located in one directory

#### Demo README Best Practices

Each demo's `examples/README.md` should include:

| Section | Purpose |
|---------|---------|
| **Use Case** | What the demo demonstrates |
| **Dataset Overview** | Document categories and languages |
| **Scoring Methodology** | How relevance weights were assigned |
| **Document Inventory** | Tiered list with scores |
| **Key Entities** | Expected extraction results (persons, organizations, locations) |
| **Demo Walkthrough** | Sequential questions for guided exploration |
| **Troubleshooting** | Common issues and solutions |

#### Example: Nazi Rat Lines Demo

> **Note:** This is an example of the current demo dataset. Demo content may change over time. Always check `examples/` for the current available demos.

The Rat Lines demo demonstrates OSINT analysis on historical intelligence documents (Nazi escape routes to South America, 1945-1960s). It includes:

- **17 source documents** in German, English, and Portuguese
- **Relevance scoring** (10-100) based on entity density and geolocation potential
- **Multimedia package**: podcasts, video walkthrough, PDF presentation
- **9-question guided walkthrough** progressing from entity identification to multi-agent debate

This demo showcases: entity extraction (GLiNER), geospatial mapping (Mapbox), network visualization (vis-network), and the courthouse debate system.

#### Multimedia Integration Pattern

Multimedia assets (audio, video, PDF) remain in `examples/multimedia/` but are documented in `docs/demos/[demo-name]/multimedia/`:

```text
# In docs/demos/[demo-name]/multimedia/audio.md

## Audio Content

### Podcast: [Title]

**Duration**: ~9 minutes | **Language**: Italian

**Summary**: This podcast explains IntellyWeave's OSINT capabilities,
covering entity extraction, the courthouse debate system, and
visualization features.

**Key Topics**:
- 7 entity types (persons, organizations, locations, events, dates, laws, cryptonyms)
- Multi-agent reasoning architecture
- Geospatial intelligence mapping

**File**: `examples/multimedia/audio/[filename].mp3`
**Transcript**: `examples/multimedia/audio/[filename]_transcription_IT.txt`
```

This pattern keeps large binary files out of `docs/` while providing discoverable documentation.

---

## Part 3: GitHub Best Practices

From [Top 10 GitHub Project Setup Tricks (2025)](https://devopstoolkit.live/development/top-10-github-project-setup-tricks-you-must-use-in-2025):

### 1. Issue Templates with Contact Links

`.github/ISSUE_TEMPLATE/config.yml` guides users to appropriate channels before filing issues.

**What it does:** Disables blank issues and provides contact links for discussions, documentation, support resources, and security vulnerability reporting. Filters noise and establishes clear processes.

✅ **Implemented**

### 2. Structured Bug Reports

`.github/ISSUE_TEMPLATE/bug_report.yml` with mandatory fields including bug description, reproduction steps, expected versus actual behavior, and environment details.

> "Mark which ones are mandatory, provide short explanations for each, and include helpful guidance before they start filling it out."

✅ **Implemented**

### 3. Feature Requests with Problem Focus

`.github/ISSUE_TEMPLATE/feature_request.yml` emphasizing problem statements over wish lists.

> "Nice to have is not a strong use case. Please explain the specific problem this feature would solve."

✅ **Implemented**

### 4. Pull Request Templates

`.github/PULL_REQUEST_TEMPLATE.md` covering: description, related issues, type of change, conventional commit formatting, testing checklist, documentation updates, security considerations, breaking changes, and DCO sign-off.

✅ **Implemented**

### 5. Conventional Commits

Enforce commit message standards like `feat(scope): description` for automated changelog generation. Breaking changes use syntax: `feat(api)!: remove deprecated endpoints`.

✅ **In AGENTS.md**

### 6. CODEOWNERS

`.github/CODEOWNERS` automatically assigns reviewers based on file paths modified. Define path-specific owners like `/docs/ @docs-team` or global defaults using `* @maintainer`.

✅ **Implemented**

### 7. Automated Release Notes

`.github/release.yml` categorizes merged PRs by labels into sections like Breaking Changes, New Features, Bug Fixes, Documentation, and Dependencies.

✅ **Implemented**

### 8. Automated PR Labeling

`.github/workflows/labeler.yml` with `.github/labeler.yml` configuration automatically assigns labels based on changed file paths.

✅ **Implemented**

### 9. OpenSSF Scorecard

`.github/workflows/scorecard.yml` evaluates security posture against best practices including dependency pinning, code review requirements, and SAST analysis.

✅ **Implemented**

### 10. Renovate

`renovate.json` automatically creates PRs for dependency updates with automerge rules, grouping, and scheduling.

> "You get pull requests created automatically, and all you have to do is either merge them yourself or...let them merge automatically."

⚠️ **Not yet implemented**

---

## Part 4: Project Setup Reference

This section documents the `projectSetup` workflow for future repositories or audits.

### Workflow Steps

#### Step 1: Check System Status

```text
Tool: mcp__dot-ai__version
```

Confirms MCP server is healthy and capabilities available.

#### Step 2: Discover Available Scopes

```json
{
  "tool": "mcp__dot-ai__projectSetup",
  "parameters": { "step": "discover" }
}
```

**Returns:**

- `sessionId` - Required for subsequent calls
- `filesToCheck` - 21 files to scan for
- `availableScopes` - 9 scopes:
  - `readme`, `legal`, `governance`, `community`
  - `github-issues`, `pr-template`, `github-community`
  - `github-security`, `github-automation`

#### Step 3: Scan Repository & Report

```bash
# Check which files exist (use Glob tool)
```

Then report findings:

```json
{
  "tool": "mcp__dot-ai__projectSetup",
  "parameters": {
    "step": "reportScan",
    "sessionId": "<from step 2>",
    "existingFiles": ["README.md", "LICENSE"]
  }
}
```

**Returns:** Gap analysis showing complete/incomplete scopes

#### Step 4: Select Scopes to Generate

```json
{
  "tool": "mcp__dot-ai__projectSetup",
  "parameters": {
    "step": "reportScan",
    "sessionId": "<from step 2>",
    "existingFiles": ["README.md"],
    "selectedScopes": ["governance", "github-issues"]
  }
}
```

#### Step 5: ⚠️ CRITICAL - Ask User Before Answering Questions

**DO NOT fill in answers automatically.** Ask the user:

| Question Type | Must Ask User |
|---------------|---------------|
| Email addresses | Yes |
| Commercial support | Yes |
| Maintainer info | Yes |
| Funding/sponsors | Yes |
| Schedule preferences | Yes |
| Exempt labels | Yes |

**For verification data**, use `gh` CLI:

```bash
gh api user --jq '{login, name, email}'
gh api repos/owner/repo --jq '{name, description, html_url}'
```

#### Step 6: Generate Scope with Answers

```json
{
  "tool": "mcp__dot-ai__projectSetup",
  "parameters": {
    "step": "generateScope",
    "sessionId": "<from step 2>",
    "scope": "governance",
    "answers": {
      "projectName": "...",
      "maintainerEmail": "..."
    }
  }
}
```

#### Step 7: ⚠️ CRITICAL - Review Before Writing

**Before writing ANY generated file:**

1. **Read the content** - Look for boilerplate that doesn't match reality
2. **Check for empty values** - MCP sometimes returns incomplete templates
3. **Remove aspirational language** - "used worldwide" when you have 1 adopter
4. **Verify config syntax** - Compare against reference from `gh api`

#### Step 8: Write Files

Only after review, use `Write` tool to create files.

### Scope Reference

| Scope | Files | Questions to Ask User |
|-------|-------|----------------------|
| `legal` | LICENSE | License type, copyright holder, year |
| `governance` | CODE_OF_CONDUCT.md, CONTRIBUTING.md, SECURITY.md, docs/MAINTAINERS.md, docs/GOVERNANCE.md, docs/ROADMAP.md | Emails, maintainer name/username, DCO requirement |
| `community` | SUPPORT.md, ADOPTERS.md | Commercial support available?, Support provider, First adopter info |
| `github-issues` | bug_report.yml, feature_request.yml, config.yml | Project name, repo URL |
| `pr-template` | PULL_REQUEST_TEMPLATE.md | DCO, conventional commits, security checklist |
| `github-community` | CODEOWNERS, release.yml, FUNDING.yml | Code owners, funding platforms |
| `github-security` | workflows/scorecard.yml | Branch name |
| `github-automation` | renovate.json, labeler.yml, workflows/labeler.yml, workflows/stale.yml | Schedule, assignees, auto-merge, exempt labels |

---

## Part 5: dot-ai Repository Reference

If you have a local clone of [vfarcic/dot-ai](https://github.com/vfarcic/dot-ai), it contains:

| Directory | Contents |
|-----------|----------|
| `shared-prompts/` | 9 MCP prompts (served via MCP server) |
| `prds/` | Example PRD files |
| `docs/guides/` | Feature guides |
| `.claude/commands/` | Eval and dev commands |

**Note:** The shared prompts are served directly by the MCP server - you don't need to copy them. They're available as `/dot-ai:*` slash commands.

---

## Resources

### DevOps Toolkit Blog (devopstoolkit.live)

| Article | Topic |
|---------|-------|
| [Top 10 GitHub Project Setup Tricks](https://devopstoolkit.live/development/top-10-github-project-setup-tricks-you-must-use-in-2025) | Repository governance automation |
| [Prompts as Production Code](https://devopstoolkit.live/ai/stop-wasting-time-turn-ai-prompts-into-production-code) | MCP prompt distribution |
| [Teaching AI Company Policies](https://devopstoolkit.live/ai/teaching-ai-your-company-policies-vector-search-enforcement) | Knowledge management with vector search |
| [Vector DBs + RAG](https://devopstoolkit.live/ai/stop-blaming-ai-vector-dbs-rag-game-changer) | Reducing AI hallucinations |
| [Context7 Solves LLMs' Biggest Flaw](https://devopstoolkit.live/ai/outdated-ai-responses-context7-solves-llms-biggest-flaw) | Keeping AI current |

### GitHub Repositories

| Repository | Purpose |
|------------|---------|
| [vfarcic/dot-ai](https://github.com/vfarcic/dot-ai) | DevOps AI Toolkit source |
| [vfarcic/devopstoolkit-live](https://github.com/vfarcic/devopstoolkit-live) | Blog source (Hugo) |

### Official Documentation

| Guide | Description |
|-------|-------------|
| [dot-ai Quick Start](https://github.com/vfarcic/dot-ai/blob/main/docs/quick-start.md) | Getting started |
| [MCP Tools Overview](https://github.com/vfarcic/dot-ai/blob/main/docs/guides/mcp-tools-overview.md) | All available tools |
| [PRD Prompts Guide](https://github.com/vfarcic/dot-ai/blob/main/docs/guides/mcp-prompts-guide.md) | Shared prompts usage |
| [Project Setup Guide](https://github.com/vfarcic/dot-ai/blob/main/docs/guides/mcp-project-setup-guide.md) | Repository governance |
