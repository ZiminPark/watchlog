#!/bin/bash

echo "🚀 Starting WatchLog Insights Servers..."

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Port $1 is already in use"
        return 1
    else
        return 0
    fi
}

# Start backend server
echo "📡 Starting Backend Server..."
cd backend


# Install dependencies
echo "📦 Installing backend dependencies..."
uv sync

# Check if port 8000 is available
if check_port 8000; then
    echo "✅ Starting backend on http://localhost:8000"
    python main.py &
    BACKEND_PID=$!
    echo "Backend PID: $BACKEND_PID"
else
    echo "❌ Backend port 8000 is already in use"
    exit 1
fi

# Wait a moment for backend to start
sleep 3

# Start frontend server
echo "🎨 Starting Frontend Server..."
cd ../frontend

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Check if port 3000 is available
if check_port 3000; then
    echo "✅ Starting frontend on http://localhost:3000"
    npm run dev &
    FRONTEND_PID=$!
    echo "Frontend PID: $FRONTEND_PID"
else
    echo "❌ Frontend port 3000 is already in use"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo ""
echo "🎉 WatchLog Insights is running!"
echo "📊 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Servers stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for both processes
wait 