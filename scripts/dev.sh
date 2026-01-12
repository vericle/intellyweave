#!/bin/bash

# Elysia Development Runner
# This script runs both the frontend (Next.js) and backend (FastAPI) in development mode

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Elysia Development Environment${NC}"
echo -e "${YELLOW}This will run both frontend (Next.js) and backend (FastAPI) servers${NC}"
echo ""

# Get repository root
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

# Check if we're in the right directory
if [ ! -d "frontend" ] || [ ! -d "backend" ]; then
    echo -e "${RED}Error: Please run this script from the repository root directory${NC}"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js is not installed. Please install Node.js 18+${NC}"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python is not installed. Please install Python 3.11+${NC}"
    exit 1
fi

# Set environment variables
export NODE_ENV=development
export NEXTJS_DEV_URL="http://localhost:3000"

echo -e "${GREEN}✓ Environment configured for development${NC}"
echo -e "  - NODE_ENV=development"
echo -e "  - NEXTJS_DEV_URL=http://localhost:3000"
echo ""

# Function to cleanup background processes
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down development servers...${NC}"
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        echo -e "${GREEN}✓ Frontend server stopped${NC}"
    fi
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        echo -e "${GREEN}✓ Backend server stopped${NC}"
    fi
    exit 0
}

# Function to check and free port
check_and_free_port() {
    local port=$1
    local pid=$(lsof -t -i:$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        echo -e "${YELLOW}Port $port is in use by PID $pid. Killing process...${NC}"
        kill -9 $pid 2>/dev/null || true
        sleep 2
    fi
}

# Check and free ports
check_and_free_port 8000
check_and_free_port 3000

echo -e "${BLUE}Cleaning backend __pycache__ directories...${NC}"
find backend -name "__pycache__" -type d -prune -exec rm -rf {} +

# Start frontend in background
echo -e "${BLUE}Starting Next.js frontend server...${NC}"
cd frontend
pnpm dev &
FRONTEND_PID=$!
cd ..
echo -e "${GREEN}✓ Frontend server started (PID: $FRONTEND_PID)${NC}"

# Wait a moment for frontend to start
sleep 3

# Start backend in background
echo -e "${BLUE}Starting FastAPI backend server...${NC}"
cd backend
source .venv/bin/activate
export PYTHONWARNINGS="ignore::ResourceWarning,ignore::DeprecationWarning"
python -m elysia.api.cli start --port 8000 --host localhost --reload false &
BACKEND_PID=$!
cd ..
echo -e "${GREEN}✓ Backend server started (PID: $BACKEND_PID)${NC}"

echo ""
echo -e "${GREEN}🎉 Development servers are running!${NC}"
echo -e "${BLUE}Frontend:${NC} http://localhost:3000"
echo -e "${BLUE}Backend API:${NC} http://localhost:8000"
echo -e "${BLUE}Health check:${NC} http://localhost:8000/api/health"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop both servers${NC}"

# Wait for background processes
wait