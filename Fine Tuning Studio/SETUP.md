# Fine-Tuning Studio - Setup Guide

Complete setup instructions for Phase 1 implementation.

## Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- pip and npm package managers
- PostgreSQL (for production) or SQLite (for development)
- Redis (optional, for async tasks)
- CUDA 11.8+ (for GPU support)

## Backend Setup

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` to configure:
- Database URL (default: SQLite)
- JWT secret key
- Redis URL (if using Redis)
- GPU settings

### 4. Initialize Database

```bash
python init_db.py
```

This will:
- Create database tables
- Create admin user (admin/admin123)
- Add default model configurations

### 5. Run Backend Server

```bash
python run.py
```

Server will start at `http://localhost:5000`

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` to set API URL:
```
REACT_APP_API_URL=http://localhost:5000/api
```

### 3. Start Development Server

```bash
npm start
```

Frontend will start at `http://localhost:3000`

## Docker Setup

### Build and Run with Docker Compose

```bash
docker-compose up -d
```

Services:
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- Backend: http://localhost:5000
- Frontend: http://localhost:3000

To stop services:
```bash
docker-compose down
```

## Verification

### 1. Backend Health Check

```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Fine-Tuning Studio API"
}
```

### 2. Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

### 3. List Models

```bash
curl http://localhost:5000/api/models/supported
```

## Running Tests

### Backend Tests

```bash
cd backend
pytest tests/
```

For verbose output:
```bash
pytest tests/ -v
```

For coverage:
```bash
pytest tests/ --cov=app
```

### Frontend Tests

```bash
cd frontend
npm test
```

## Development Workflow

### Making Changes

1. **Backend changes**: Edit files in `backend/app/`
   - Restart server: `python run.py`
   - Server auto-reloads in development mode

2. **Frontend changes**: Edit files in `frontend/src/`
   - Frontend auto-reloads on file save

### Database Migrations

For major schema changes:
1. Update model in `backend/app/models/`
2. Create backup of existing database
3. Delete `finetuning_studio.db` (or use Alembic for production)
4. Run `python init_db.py`

## Troubleshooting

### Port Already in Use

If port 5000 is in use:
```bash
# On Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# On macOS/Linux
lsof -i :5000
kill -9 <PID>
```

### Database Connection Error

Ensure SQLite file is writable:
```bash
chmod 666 finetuning_studio.db
```

### Frontend API Connection Error

Check that:
1. Backend is running on port 5000
2. REACT_APP_API_URL is set correctly
3. CORS is enabled in backend

### GPU Not Detected

Set environment variable:
```bash
export USE_GPU=false  # Use CPU only
```

## Next Steps

- Proceed to Phase 2: Dataset & Training Management
- Add more model configurations in database
- Set up Redis for async task processing
- Configure PostgreSQL for production

## Support

For issues:
1. Check logs in `backend/logs/`
2. Verify environment variables
3. Check that all prerequisites are installed
4. Run `docker-compose logs` for Docker issues
