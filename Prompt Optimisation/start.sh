#!/bin/bash

echo "Starting Prompt Optimization Platform..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if node is installed for frontend (optional)
if ! command -v node &> /dev/null; then
    echo "Note: Node.js not found. Frontend will still work with just a browser."
fi

# Install backend dependencies
echo "Installing backend dependencies..."
cd backend
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Please edit backend/.env with your settings"
fi

# Run migrations and start backend
echo "Starting backend server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &

cd ..

# Display frontend instructions
echo ""
echo "=========================================="
echo "✅ Prompt Optimization Platform is starting!"
echo "=========================================="
echo ""
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "To start the frontend:"
echo "  1. cd frontend"
echo "  2. python -m http.server 8001"
echo "  3. Visit http://localhost:8001"
echo ""
echo "Or simply open frontend/index.html in your browser"
echo ""
echo "To run tests:"
echo "  cd backend && pytest tests/ -v"
echo ""
echo "=========================================="
