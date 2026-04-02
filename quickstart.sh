#!/bin/bash
# Quick start script for IncidentCommander

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         IncidentCommander OpenEnv Environment             ║"
echo "║                  Quick Start Script                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version found"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "📚 Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Run validation
echo "🧪 Running validation checks..."
python validate.py
echo ""

# Start server
echo "🚀 Starting IncidentCommander server..."
echo "   Server will be available at: http://localhost:7860"
echo "   Health check: curl http://localhost:7860/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python -m uvicorn app:app --host 0.0.0.0 --port 7860 --reload
