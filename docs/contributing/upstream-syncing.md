# Syncing with Upstream

Quick reference for pulling updates from Weaviate's repositories.

## Quick Sync

```bash
# Backend
git fetch upstream-backend main
git subtree pull --prefix=backend upstream-backend main --squash

# Frontend
git fetch upstream-frontend main
git subtree pull --prefix=frontend upstream-frontend main --squash

# Rebuild
scripts/build.sh
```

## Governance File Management

IntellyWeave uses `.gitattributes` with the `merge=ours` strategy to prevent upstream governance files from reappearing during syncs.

### What Gets Automatically Excluded

The following upstream files are **automatically excluded** during subtree pulls:

- `backend/.github/ISSUE_TEMPLATE/` - Upstream issue templates
- `backend/.github/pull_request_template.md` - Upstream PR template
- `backend/CONTRIBUTING.md` - Upstream contributing guidelines
- `frontend/.github/workflows/notify-backend.yml` - Upstream-specific workflow

These files are managed in `.gitattributes`:

```gitattributes
backend/.github/ISSUE_TEMPLATE/** merge=ours
backend/.github/pull_request_template.md merge=ours
backend/CONTRIBUTING.md merge=ours
frontend/.github/workflows/notify-backend.yml merge=ours
```

### What Gets Kept from Upstream

**Backend workflows** are kept because they provide functional value:

- `backend/.github/workflows/docs.yml` - MkDocs documentation generation
- `backend/.github/workflows/run_pytest.yml` - Backend test runner
- `backend/.github/workflows/pypi-release.yml` - Safe to keep (only runs for weaviate org)
- `backend/.github/workflows/frontend_release.yml` - Frontend auto-update workflow

**README files** are kept to document the Elysia components:

- `backend/README.md` - Elysia backend documentation
- `frontend/README.md` - Elysia frontend documentation

### Verifying After Sync

After pulling from upstream, verify governance files remain excluded:

```bash
# These should NOT exist (return "No such file or directory")
ls backend/.github/ISSUE_TEMPLATE/
ls backend/CONTRIBUTING.md
ls frontend/.github/workflows/notify-backend.yml

# These SHOULD exist
ls backend/.github/workflows/docs.yml
ls backend/.github/workflows/run_pytest.yml
ls backend/README.md
```

If any excluded files reappear, the `.gitattributes` configuration may need adjustment.

## Handling Conflicts

If conflicts occur during subtree pull:

1. `git status` to see conflicted files
2. Open files and resolve conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)
3. For governance files: Choose IntellyWeave's version (ours)
4. For functional code: Carefully merge both changes
5. `git add <resolved-file>`
6. `git commit`

### Common Conflict Scenarios

**Scenario 1: Governance file appears despite `.gitattributes`**

This shouldn't happen with proper configuration, but if it does:

```bash
# Remove the file
rm backend/CONTRIBUTING.md

# Stage the deletion
git add backend/CONTRIBUTING.md

# Complete the merge
git commit
```

**Scenario 2: Workflow file conflicts**

Keep functional workflows, remove governance-only workflows:

```bash
# Keep functional
git checkout --ours backend/.github/workflows/docs.yml

# Remove upstream-specific
git rm frontend/.github/workflows/notify-backend.yml

git add .
git commit
```

## Testing After Sync

```bash
cd backend && source .venv/bin/activate && pip install -e .
cd ../frontend && pnpm install
cd .. && scripts/build.sh
```

Done. Test at <http://localhost:8000>

## Troubleshooting

### Problem: "Upstream governance files keep reappearing"

**Solution**: Verify `.gitattributes` exists and contains correct merge strategies:

```bash
cat .gitattributes | grep "merge=ours"
```

Should show:
```
backend/.github/ISSUE_TEMPLATE/** merge=ours
backend/.github/pull_request_template.md merge=ours
backend/CONTRIBUTING.md merge=ours
frontend/.github/workflows/notify-backend.yml merge=ours
```

### Problem: "Merge strategy not working"

**Solution**: Ensure merge strategy is configured in git:

```bash
git config merge.ours.driver true
```

This is usually automatic, but may need manual setup in some environments.

### Problem: "I accidentally merged an upstream governance file"

**Solution**: Remove it and re-commit:

```bash
git rm backend/CONTRIBUTING.md
git commit -m "chore: remove upstream governance file"
```

The `.gitattributes` configuration will prevent it from reappearing in future syncs.
