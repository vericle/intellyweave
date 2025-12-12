# Contributing Guide

This document covers how to contribute to this private Elysia fork and how to contribute changes back to the upstream Weaviate repositories.

## Working on This Private Fork

### Creating Features

1. **Create a feature branch**

```bash
git checkout -b feature/my-feature-name
```

2. **Make your changes** in `backend/` or `frontend/`

3. **Test your changes**

```bash
# Build and test
scripts/build.sh

# Run backend tests (if available)
cd backend
source .venv/bin/activate
pytest tests/

# Test frontend builds
cd frontend
pnpm run build
```

3. **Document custom modifications**

Track your changes in `docs/custom-changes.md` for future reference:

- What was changed
- Why it was changed
- Potential upstream impact

5. **Commit and push**

```bash
git add .
git commit -m "feat: descriptive message about your change"
git push origin feature/my-feature-name
```

### Commit Message Convention

Use conventional commits for clarity:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Examples:

```bash
feat: add custom authentication handler
fix: resolve WebSocket connection timeout
docs: update setup instructions
```

## Syncing with Upstream

Before starting new work, sync with upstream to avoid conflicts:

```bash
# Sync backend
git fetch upstream-backend main
git subtree pull --prefix=backend upstream-backend main --squash

# Sync frontend
git fetch upstream-frontend main
git subtree pull --prefix=frontend upstream-frontend main --squash

# Rebuild and test
scripts/build.sh
```

### Handling Merge Conflicts

If conflicts occur during upstream sync:

1. Git will pause and show conflicted files
2. Open each file and resolve conflicts manually
3. Look for conflict markers:

   ```bash
   <<<<<<< HEAD
   Your changes
   =======
   Upstream changes
   >>>>>>> ...
   ```

4. Edit to keep desired changes
5. Stage resolved files: `git add <file>`
6. Complete merge: `git commit`

See [docs/syncing.md](docs/syncing.md) for detailed conflict resolution strategies.

## Contributing Back to Upstream

If you've made improvements that would benefit the community, consider contributing them back to Weaviate's repositories.

### Prerequisites

1. **Fork the upstream repository** on GitHub
   - Backend: Fork <https://github.com/weaviate/elysia>
   - Frontend: Fork <https://github.com/weaviate/elysia-frontend>

2. **Add your fork as a remote**

```bash
# For backend contributions
git remote add my-fork-backend git@github.com:YOUR-USERNAME/elysia.git

# For frontend contributions
git remote add my-fork-frontend git@github.com:YOUR-USERNAME/elysia-frontend.git
```

### Submitting Backend Changes

1. **Extract your backend changes to a branch**

```bash
# Create a branch for your changes
git checkout -b upstream-feature/my-contribution

# Split out backend changes
git subtree push --prefix=backend my-fork-backend my-contribution
```

2. **Create Pull Request**
   - Go to your fork on GitHub
   - Click "New Pull Request"
   - Select `weaviate/elysia` as base repository
   - Write clear description of your changes
   - Submit PR

### Submitting Frontend Changes

Same process as backend, but for frontend:

```bash
git checkout -b upstream-feature/my-frontend-contribution
git subtree push --prefix=frontend my-fork-frontend my-frontend-contribution
```

Then create PR from your fork to `weaviate/elysia-frontend`.

## Best Practices

### Keep Custom Changes Isolated

When possible, add custom functionality in separate files rather than modifying upstream code heavily:

```python
# Good: New file for custom features
# backend/elysia/custom/my_feature.py

# Less ideal: Heavy modifications to upstream files
# backend/elysia/api/main.py (many custom changes)
```

### Document Custom Code

Mark custom modifications clearly:

```python
# CUSTOM: Added support for custom authentication
def custom_auth_handler():
    # Your code here
    pass
```

```javascript
// CUSTOM: Modified to support additional API endpoint
const customEndpoint = '/api/custom';
```

### Use Feature Flags

For experimental features, use environment variables or feature flags:

```python
# backend/.env
ENABLE_CUSTOM_FEATURE=true

# In code
if os.getenv('ENABLE_CUSTOM_FEATURE') == 'true':
    # Custom feature logic
```

### Test Before Committing

Always test your changes:

```bash
# Full build
scripts/build.sh

# Backend tests
cd backend && source .venv/bin/activate && pytest tests/

# Frontend build
cd frontend && pnpm run build

# Integration test
cd backend && elysia start
# Verify at http://localhost:8000
```

## Code Review Process

### For Internal Changes

1. Create feature branch
2. Make changes and test
3. Push to origin
4. Create pull request (if using GitHub flow)
5. Review and merge

### For Team Collaboration

If working with a team on this private fork:

- Use pull requests for code review
- Require at least one approval
- Run automated tests if configured
- Keep branches short-lived (1-2 weeks max)

## Troubleshooting Contributions

### "Can't push to upstream"

You need write access to upstream repositories. Instead:

1. Fork the repository
2. Push to your fork
3. Create PR from your fork

### "Subtree push creates too many commits"

This is normal. Subtree push includes all relevant history. The upstream maintainers will squash if needed.

### "Changes conflict with upstream"

This means upstream has evolved. Options:

1. Rebase your changes on latest upstream
2. Resolve conflicts manually
3. Consider if your change is still relevant

## Getting Help

- **Upstream Issues**: Check upstream GitHub issues first
- **Documentation**: See [docs/](docs/) directory
- **Community**: Weaviate Discord or GitHub Discussions

## Code of Conduct

When contributing upstream, follow Weaviate's code of conduct and contribution guidelines:

- Be respectful and constructive
- Write clear, documented code
- Include tests for new features
- Follow existing code style

## Questions?

If you're unsure about contributing a change upstream:

1. Open an issue in the upstream repository first
2. Discuss your proposed changes
3. Get feedback before implementing
4. This saves time and increases acceptance likelihood
