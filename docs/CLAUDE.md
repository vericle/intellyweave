# Documentation Directory - Claude Code Instructions

## Documentation Standards & Format

### File Structure Requirements

- **Filename format**: Use kebab-case with descriptive names (`agent-overview.md`, `setup/docker-setup.md`)
- **Directory organization**: Group related docs in subdirectories (`setup/`, guides, references)
- **Consistent naming**: Use prefix patterns (`backend-` for backend-related guides,  `setup-` or directory structure for setup guides)

### Documentation Format Standards

- **H1 Title**: One H1 per file with descriptive title and bold summary line
- **Overview section**: Always include "What it does", "Use when", and "📖 Full Guide" links where applicable
- **Table format**: Use comparison tables for method/option comparisons with Pros/Cons/Best For columns
- **Status indicators**: Use emoji indicators (✅ ❌ 🎯 🚀 🔧) for recommendations and status
- **Code blocks**: Always use syntax highlighting (```bash,```yaml, ```json)
- **Cross-references**: Link related documentation with relative paths
- **Decision trees**: Use clear "🎯 Recommended" and alternative flow patterns

### Command and Example Validation Rules

**🚨 CRITICAL REQUIREMENT: All commands and examples MUST be validated before inclusion**

#### For Shell Commands

- **Run every command** in a test environment before documenting
- **Include actual output** where relevant (truncated if very long)
- **Test with different environments** if the command is environment-dependent
- **Verify prerequisites** by testing without required dependencies

#### For Configuration Examples

- **Test configuration files** to ensure they work as documented
- **Validate YAML/JSON syntax** using parsers
- **Test with realistic values** not just placeholder examples

### Content Quality Standards

- **Accuracy first**: Never guess command syntax or outputs - always verify
- **Real examples**: Use actual working examples from testing, not theoretical ones
- **Current information**: Verify feature availability and syntax before documenting
- **User perspective**: Write from the user's workflow perspective, not implementation details

### README.md Coordination

- **Keep README.md current**: When adding new major features or setup methods to docs, update the root README.md
- **Maintain consistency**: Ensure terminology and descriptions match between README.md and detailed docs
- **Update cross-references**: When restructuring docs, update README.md links
- **Sync feature lists**: Major feature additions should be reflected in both README.md overview and detailed guides

### Validation Workflow

**🚨 MANDATORY: Execute-then-document, one item at a time.**

For each command/example in documentation:
1. Execute it and capture actual output
2. Document that item with real output
3. Move to next item and repeat

**NEVER** batch-write multiple examples then test afterward. Validate each step before proceeding to the next.

### Common Mistakes to Avoid

- ❌ Adding command examples without testing them first
- ❌ Using outdated or deprecated syntax
- ❌ Copying examples from other projects without validation
- ❌ Assuming MCP tool parameters or outputs without testing, reference official docs or asking the user
- ❌ Forgetting to update README.md when adding major new documentation
- ❌ Using placeholder text instead of real examples
- ❌ Including debugging commands users won't actually run

Remember: Documentation credibility depends on accuracy. One broken example undermines trust in the entire guide.
