#!/bin/bash

set -e

# Get the repository root directory (parent of scripts/)
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=========================================="
echo "Elysia Combined Repository Setup"
echo "=========================================="
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.11 or 3.12."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Detected Python version: $PYTHON_VERSION"

if [[ "$PYTHON_VERSION" < "3.11" ]] || [[ "$PYTHON_VERSION" > "3.12" ]]; then
    echo "Warning: Elysia requires Python 3.11 or 3.12. You have $PYTHON_VERSION"
    echo "Continuing anyway, but you may encounter issues."
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
echo "Detected Node.js version: $NODE_VERSION"

if [[ "$NODE_VERSION" -lt 18 ]]; then
    echo "Warning: Node.js 18+ is recommended. You have version $NODE_VERSION"
    echo "Continuing anyway, but you may encounter issues."
fi

echo ""
echo "=========================================="
echo "Step 1/3: Setting up Backend"
echo "=========================================="

cd "$REPO_ROOT/backend"

# Create virtual environment
echo "Creating Python virtual environment..."
python3.12 -m venv .venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install backend dependencies
echo "Installing backend dependencies (this may take a few minutes)..."
pip install --upgrade pip
pip install -e .

# Copy environment example if it doesn't exist
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo "Creating .env file from .env.example..."
        cp .env.example .env
        echo ""
        echo "⚠️  IMPORTANT: Edit backend/.env with your API keys and configuration!"
        echo ""
    else
        echo "Warning: No .env.example found. You'll need to create .env manually."
    fi
else
    echo ".env file already exists, skipping."
fi

echo "Backend setup complete!"
echo ""

# Deactivate virtual environment
deactivate

echo "=========================================="
echo "Step 2/3: Setting up Frontend"
echo "=========================================="

cd "$REPO_ROOT/frontend"

# Install frontend dependencies
echo "Installing frontend dependencies (this may take a few minutes)..."
pnpm install

# Copy environment example if it doesn't exist and example exists
if [ ! -f .env.local ] && [ -f .env.example ]; then
    echo "Creating .env.local file from .env.example..."
    cp .env.example .env.local
fi

echo "Frontend setup complete!"
echo ""

cd "$REPO_ROOT"

echo "=========================================="
echo "Step 3/3: Building Application"
echo "=========================================="

# Ask if user wants to build now
read -p "Do you want to build the application now? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    "$REPO_ROOT/scripts/build.sh"
    echo ""
    echo "Build complete!"
else
    echo "Skipping build. You can run 'scripts/build.sh' later."
fi

echo ""
echo "=========================================="
echo "Setup Complete! 🎉"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Edit backend/.env with your API keys:"
echo "   - WEAVIATE_URL"
echo "   - WEAVIATE_API_KEY"
echo "   - OPENAI_API_KEY"
echo "   - ANTHROPIC_API_KEY (optional)"
echo ""
echo "2. Start the backend:"
echo "   cd backend"
echo "   source .venv/bin/activate"
echo "   elysia start"
echo ""
echo "3. Access the application at http://localhost:8000"
echo ""
echo "For development commands, see CLAUDE.md (Build & Commands section)"
echo "For syncing with upstream, see docs/syncing.md"
echo ""
