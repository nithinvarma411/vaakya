#!/bin/bash

# Code Quality Check Script for Vaakya
# Runs all code quality tools and reports results

echo "🔍 Running Code Quality Checks for Vaakya..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
        source .venv/bin/activate
    elif [[ "$OSTYPE" == "msys"* ]] || [[ "$OSTYPE" == "cygwin"* ]]; then
        source .venv/Scripts/activate
    fi
    echo "✅ Virtual environment activated"
fi

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo ""
echo "🧹 Running Ruff Auto-fix..."
ruff check --fix src/

echo ""
echo "🎨 Running Ruff Formatting..."
ruff format src/

echo ""
echo "🧹 Running Ruff Linting (checking for remaining issues)..."
if ! ruff check src/; then
    echo ""
    echo "❌ Ruff found issues that need to be addressed manually"
    exit 1
fi

echo ""
echo "🔍 Running MyPy Type Checking..."
if ! mypy src; then
    echo ""
    echo "❌ MyPy found type checking issues"
    exit 1
fi

echo ""
echo "✅ All code quality checks passed!"
echo "📝 Note: Test scripts are excluded from quality checks (focus on src/ folder only)"