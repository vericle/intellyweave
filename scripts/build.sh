#!/bin/bash

set -e

# Get the repository root directory (parent of scripts/)
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "==================================="
echo "Building Elysia Combined Repository"
echo "==================================="

# Build frontend
echo ""
echo "Step 1: Building frontend..."
cd "$REPO_ROOT/frontend"
pnpm install
pnpm run build
echo "Frontend build complete!"

# Export frontend to backend
echo ""
echo "Step 2: Exporting frontend to backend..."
./export.sh
echo "Frontend export complete!"

# Return to root
cd "$REPO_ROOT"

echo ""
echo "==================================="
echo "Build completed successfully!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. cd backend"
echo "2. python3.13 -m venv .venv"
echo "3. source .venv/bin/activate"
echo "4. pip install -e ."
echo "5. elysia start"
