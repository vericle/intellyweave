# Git Subtree Governance Structure

**IntellyWeave's approach to managing governance files across git subtrees**

## Overview

IntellyWeave tracks two upstream repositories as git subtrees:

- **backend/** ← [weaviate/elysia](https://github.com/weaviate/elysia)
- **frontend/** ← [weaviate/elysia-frontend](https://github.com/weaviate/elysia-frontend)

This creates a challenge: **upstream governance files conflict with IntellyWeave's own governance**.

## The Problem

Upstream subtree directories contain their own governance files:

- Issue templates pointing to weaviate/elysia
- PR templates referencing Weaviate's contributing guidelines
- CONTRIBUTING.md mentioning danny@weaviate.io
- Workflows designed for Weaviate's CI/CD pipelines

**Result**: Contributors see multiple sets of templates and get confused about where to submit issues.

## The Solution

**Three-layer approach:**

1. **Remove conflicting upstream governance files**
2. **Use `.gitattributes` to prevent re-appearance during syncs**
3. **Document the structure clearly for contributors**

### Layer 1: Files Removed

```bash
# Removed from backend/
backend/.github/ISSUE_TEMPLATE/bug_report.yml
backend/.github/ISSUE_TEMPLATE/feature_request.yml
backend/.github/pull_request_template.md
backend/CONTRIBUTING.md

# Removed from frontend/
frontend/.github/workflows/notify-backend.yml
```

### Layer 2: `.gitattributes` Configuration

Located at `/home/vero/projects/vericle/intellyweave/.gitattributes`:

```gitattributes
# Git Subtree Merge Strategy
# Prevent upstream governance files from being merged during subtree pulls

# Backend governance - use "ours" strategy (keep our deletions)
backend/.github/ISSUE_TEMPLATE/** merge=ours
backend/.github/pull_request_template.md merge=ours
backend/CONTRIBUTING.md merge=ours

# Frontend governance - use "ours" strategy
frontend/.github/workflows/notify-backend.yml merge=ours
```

**How it works:**

- `merge=ours` tells git to always prefer "our" version during merges
- When upstream updates these files, git ignores the changes
- Our deletions persist across all future `git subtree pull` operations

### Layer 3: Documentation

Updated documentation in:

- `/home/vero/projects/vericle/intellyweave/CONTRIBUTING.md` - New section explaining repository structure
- `/home/vero/projects/vericle/intellyweave/docs/syncing.md` - Comprehensive guide on governance file management

## What Gets Kept vs Removed

### ✅ Kept from Upstream

**Backend workflows** (provide functional value):
- `backend/.github/workflows/docs.yml` - MkDocs documentation generation
- `backend/.github/workflows/run_pytest.yml` - Backend test runner
- `backend/.github/workflows/pypi-release.yml` - PyPI release (safe: only runs for weaviate org)
- `backend/.github/workflows/frontend_release.yml` - Frontend auto-update

**README files** (document the components):
- `backend/README.md` - Elysia backend documentation
- `frontend/README.md` - Elysia frontend documentation

### ❌ Removed (Create Confusion)

**Governance files** pointing to wrong repositories:
- Issue templates
- PR templates
- CONTRIBUTING.md files
- Upstream-specific workflows (like notify-backend.yml)

## Best Practices for Git Subtrees

### 1. Use `.gitattributes` merge strategies

The `merge=ours` strategy is perfect for subtree governance files:

```gitattributes
subtree/conflicting-file.md merge=ours
subtree/conflicting-dir/** merge=ours
```

### 2. Document what gets excluded

Make it clear to contributors which files are intentionally absent and why.

### 3. Verify after each sync

After `git subtree pull`, check that excluded files remain deleted:

```bash
ls backend/.github/ISSUE_TEMPLATE/  # Should fail
ls backend/.github/workflows/       # Should succeed
```

### 4. Keep functional content

Don't blindly remove all upstream files - keep workflows, READMEs, and technical documentation that provide value.

### 5. Centralize governance at repository root

Use root-level `.github/`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` for the main repository.

## Testing the Configuration

### Verification Commands

```bash
# Files that should NOT exist
ls backend/.github/ISSUE_TEMPLATE/ 2>&1 | grep "No such file"
ls backend/CONTRIBUTING.md 2>&1 | grep "No such file"
ls frontend/.github/workflows/notify-backend.yml 2>&1 | grep "No such file"

# Files that SHOULD exist
ls backend/.github/workflows/docs.yml
ls backend/.github/workflows/run_pytest.yml
ls backend/README.md
ls .gitattributes
```

### Test Subtree Pull

After syncing with upstream, verify the merge strategy works:

```bash
# Perform a subtree pull
git fetch upstream-backend main
git subtree pull --prefix=backend upstream-backend main --squash

# Verify governance files didn't reappear
ls backend/.github/ISSUE_TEMPLATE/  # Should still not exist
ls backend/CONTRIBUTING.md          # Should still not exist

# Verify functional files still exist
ls backend/.github/workflows/docs.yml  # Should exist
```

## Troubleshooting

### Problem: Governance files reappear after sync

**Cause**: `.gitattributes` not configured correctly or git merge strategy not enabled

**Solution**:

```bash
# Check .gitattributes
cat .gitattributes | grep "merge=ours"

# Ensure merge strategy is configured
git config merge.ours.driver true

# If files reappeared, remove them again
git rm -r backend/.github/ISSUE_TEMPLATE/
git rm backend/CONTRIBUTING.md
git commit -m "chore: remove upstream governance files"
```

### Problem: Functional workflows accidentally removed

**Cause**: Too broad `.gitattributes` patterns

**Solution**:

Be specific with patterns:

```gitattributes
# ✅ Good - specific
backend/.github/ISSUE_TEMPLATE/** merge=ours

# ❌ Bad - too broad
backend/.github/** merge=ours  # Would exclude functional workflows
```

### Problem: Merge conflicts on governance files

**Cause**: `.gitattributes` patterns don't match file paths exactly

**Solution**:

Verify patterns match actual file paths:

```bash
# Check actual paths
git ls-files backend/.github/

# Update .gitattributes patterns to match exactly
```

## Alternative Approaches Considered

### ❌ Approach 1: Manual deletion after each sync

**Problem**: Error-prone, easy to forget

### ❌ Approach 2: Git hooks to remove files

**Problem**: Hooks don't run on all operations, hard to maintain

### ❌ Approach 3: Fork upstream repositories

**Problem**: Harder to sync, loses connection to upstream

### ✅ Approach 4: `.gitattributes` with merge strategies (CHOSEN)

**Benefits**:
- Automatic and reliable
- Works across all git operations
- Standard git feature
- Easy to understand and maintain

## References

- [Git Attributes Documentation](https://git-scm.com/docs/gitattributes)
- [Git Merge Strategies](https://git-scm.com/docs/git-merge#_merge_strategies)
- [Git Subtree Command](https://git-scm.com/docs/git-subtree)
- [IntellyWeave Contributing Guide](/home/vero/projects/vericle/intellyweave/CONTRIBUTING.md)
- [IntellyWeave Syncing Guide](/home/vero/projects/vericle/intellyweave/docs/syncing.md)

## Summary

✅ **Removed** upstream governance files that create confusion
✅ **Configured** `.gitattributes` to prevent re-appearance
✅ **Kept** functional workflows and documentation from upstream
✅ **Documented** the structure for future contributors
✅ **Tested** verification commands to ensure it works

This approach provides a clean governance structure while maintaining easy syncing with upstream repositories.
