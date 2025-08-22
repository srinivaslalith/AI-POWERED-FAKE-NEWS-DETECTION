#!/bin/bash

# Comprehensive setup script for Fake News Detector
# This script handles all dependency installation and setup

set -e  # Exit on any error

echo "🚀 Setting up Fake News Detector"
echo "================================"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.8 or higher."
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js is required but not installed."
    echo "Please install Node.js 16 or higher."
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm is required but not installed."
    echo "Please install npm (usually comes with Node.js)."
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)

echo "✅ Python $PYTHON_VERSION found"
echo "✅ Node.js v$NODE_VERSION found"

# Setup backend
echo ""
echo "🐍 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv || {
        echo "❌ Failed to create virtual environment."
        echo "On Ubuntu/Debian, try: sudo apt install python3-venv"
        echo "On other systems, ensure pip and venv are installed."
        exit 1
    }
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing backend dependencies..."
pip install -r requirements.txt || {
    echo "❌ Failed to install some dependencies."
    echo "This might be due to system compatibility or network issues."
    echo "You can try installing minimal dependencies with:"
    echo "pip install -r requirements-minimal.txt"
    echo ""
    echo "Then manually install transformers and torch:"
    echo "pip install transformers torch"
    exit 1
}

echo "✅ Backend dependencies installed successfully"

# Test backend
echo "Testing backend configuration..."
python -c "from app.config import config; print(f'✅ Backend config OK: {config.model_name}')" || {
    echo "❌ Backend configuration test failed"
    exit 1
}

# Setup frontend
echo ""
echo "⚛️ Setting up frontend..."
cd ../frontend

echo "Installing frontend dependencies..."
npm install || {
    echo "❌ Failed to install frontend dependencies."
    echo "Check your Node.js version and network connection."
    exit 1
}

echo "✅ Frontend dependencies installed successfully"

# Final validation
echo ""
echo "🧪 Running final validation..."
cd ..
python3 test_basic.py || {
    echo "❌ Basic validation failed"
    exit 1
}

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "🚀 To start the application:"
echo "1. Backend (Terminal 1):"
echo "   cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo ""
echo "2. Frontend (Terminal 2):"
echo "   cd frontend && npm start"
echo ""
echo "3. Open http://localhost:3000 in your browser"
echo ""
echo "📚 Additional resources:"
echo "   - API docs: http://localhost:8000/docs"
echo "   - Test API: ./scripts/test_requests.sh"
echo "   - Quick start: ./start_demo.sh"

echo ""
echo "✅ Setup complete! Enjoy detecting fake news! 🔍"