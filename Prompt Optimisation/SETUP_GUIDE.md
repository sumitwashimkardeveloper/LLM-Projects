# Setup Guide - Prompt Optimization Platform Step 1

## Quick Start (5 minutes)

### Option 1: Local Development (Recommended for Development)

#### Prerequisites
- Python 3.8+
- pip (Python package manager)

#### Steps

1. **Install Backend Dependencies**
```bash
cd backend
pip install -r requirements.txt
cd ..
```

2. **Start Backend Server**
```bash
cd backend
python -m uvicorn app.main:app --reload
```
Backend will run at: `http://localhost:8000`

3. **Start Frontend**
Open in a new terminal:
```bash
cd frontend
python -m http.server 8001
```
Frontend will run at: `http://localhost:8001`

4. **Access the Application**
- Open browser: `http://localhost:8001`
- API Documentation: `http://localhost:8000/docs`

### Option 2: Docker (Recommended for Production)

#### Prerequisites
- Docker
- Docker Compose

#### Steps

1. **Clone/Navigate to Project**
```bash
cd "Prompt Optimisation"
```

2. **Create .env File**
```bash
cd backend
cp .env.example .env
cd ..
```

Edit `backend/.env`:
```
DATABASE_URL=postgresql://postgres:password@postgres:5432/prompt_optimization
SECRET_KEY=your-secret-key-change-this
```

3. **Start Services**
```bash
docker-compose up -d
```

4. **Access the Application**
- API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Frontend: Open `frontend/index.html` in browser

5. **Stop Services**
```bash
docker-compose down
```

## Database Setup

### Using SQLite (Development - Default)
No setup needed! Database file will be created automatically in `backend/test.db`

### Using PostgreSQL (Production Recommended)

#### Local PostgreSQL

1. **Install PostgreSQL**
```bash
# macOS
brew install postgresql

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Windows
# Download from https://www.postgresql.org/download/windows/
```

2. **Create Database**
```bash
psql -U postgres -c "CREATE DATABASE prompt_optimization;"
```

3. **Update .env**
```
DATABASE_URL=postgresql://postgres:password@localhost/prompt_optimization
```

#### Using Docker Compose
All handled automatically! Just run `docker-compose up`

## Running Tests

### Run All Tests
```bash
cd backend
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_prompts.py -v
```

### Run with Coverage Report
```bash
pytest tests/ --cov=app --cov-report=html
```

## Project Configuration

### Backend Configuration (.env)
```
# Database
DATABASE_URL=postgresql://user:password@localhost/prompt_optimization

# Security
SECRET_KEY=your-very-secret-key-minimum-32-characters
ALGORITHM=HS256

# Authentication
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Frontend Configuration (frontend/app.js)
```javascript
const API_BASE_URL = "http://localhost:8000/api";
```

If running on different ports, update this URL.

## Common Issues & Solutions

### Issue: "Connection refused" to database
**Solution:**
- Make sure PostgreSQL is running
- Check DATABASE_URL in .env
- For Docker: Wait for postgres service to be healthy

### Issue: "CORS error" in frontend
**Solution:**
- Ensure backend is running on port 8000
- Ensure frontend is running on port 8001
- Check if API_BASE_URL in app.js is correct

### Issue: "Module not found" error
**Solution:**
```bash
cd backend
pip install -r requirements.txt
```

### Issue: Port already in use
**Solution:**
```bash
# Find process using port 8000
lsof -i :8000
# Kill the process
kill -9 <PID>

# Or run on different port
uvicorn app.main:app --port 8001
```

### Issue: Authentication token expired
**Solution:**
- Log out and log back in
- Token expires based on ACCESS_TOKEN_EXPIRE_MINUTES setting

## Development Workflow

### 1. Making Changes to Backend
```bash
cd backend
# Edit files in app/
# Backend auto-reloads with --reload flag
```

### 2. Making Changes to Frontend
```bash
cd frontend
# Edit index.html and app.js
# Refresh browser to see changes
```

### 3. Adding New API Endpoints
1. Define database model in `backend/app/models.py`
2. Create Pydantic schema in `backend/app/schemas.py`
3. Create route in `backend/app/routes/`
4. Include router in `backend/app/main.py`

### 4. Testing
```bash
# Write tests in backend/tests/
# Run tests with pytest
pytest backend/tests/ -v
```

## Performance Optimization

### Database Indexing
Indexes are already created on:
- `users.email`
- `prompts.author_id`
- `prompts.id`
- `prompt_versions.prompt_id`
- `prompt_versions.version_number`

### Caching Strategy
Currently using:
- In-memory session caching
- SQLAlchemy lazy loading

Future improvements:
- Redis caching
- Query result caching

## Security Checklist

✅ Implemented:
- Password hashing with bcrypt
- JWT authentication
- Authorization checks
- SQL injection prevention
- CORS headers

For Production:
- [ ] Use HTTPS
- [ ] Set strong SECRET_KEY (32+ characters)
- [ ] Configure allowed CORS origins
- [ ] Use PostgreSQL with encrypted connections
- [ ] Enable rate limiting
- [ ] Setup monitoring and logging
- [ ] Regular security audits

## Deployment Checklist

### To AWS
1. Set up RDS PostgreSQL database
2. Deploy Docker container to ECS or EC2
3. Configure environment variables
4. Set up CloudFront for frontend
5. Enable CloudWatch monitoring

### To Heroku
```bash
# Install Heroku CLI
# Login: heroku login
# Create app: heroku create
# Set environment: heroku config:set KEY=value
# Deploy: git push heroku main
```

### To DigitalOcean
```bash
# Create Droplet with Ubuntu
# Install Docker and Docker Compose
# Clone repo and run docker-compose up
```

## Monitoring & Logging

### Enable Debug Logging
Add to `backend/app/main.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Monitor Performance
- Check API response times: `http://localhost:8000/docs`
- Monitor database queries in logs
- Use browser DevTools for frontend performance

## Next Steps

After Step 1 is complete and running:
1. Test all functionality in the UI
2. Run the test suite: `pytest tests/ -v`
3. Review the code and documentation
4. Plan Step 2: A/B Testing & Automatic Prompt Search

## Support & Troubleshooting

### Get Help
- Check the README.md for API documentation
- Review test files for usage examples
- Check API docs at http://localhost:8000/docs
- Enable debug logging for detailed error messages

### Report Issues
Include:
- Error message
- Steps to reproduce
- Environment (OS, Python version, etc.)
- Full error traceback

---

**Happy Coding!** 🚀

For questions or issues, refer to the README.md or API documentation.
