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

## Handling Conflicts

If conflicts occur:

1. `git status` to see conflicted files
2. Open files and resolve conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)
3. `git add <resolved-file>`
4. `git commit`

## Testing After Sync

```bash
cd backend && source .venv/bin/activate && pip install -e .
cd ../frontend && pnpm install
cd .. && scripts/build.sh
```

Done. Test at <http://localhost:8000>
