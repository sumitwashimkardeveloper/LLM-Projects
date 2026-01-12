# Quick Reference Guide

## 🚀 Start the Platform (30 seconds)

### Terminal 1 - Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
# Backend running at http://localhost:8000
```

### Terminal 2 - Frontend
```bash
cd frontend
python -m http.server 8001
# Frontend at http://localhost:8001
```

### Browser
Open: `http://localhost:8001`

---

## 📋 Common Tasks

### Run Tests
```bash
cd backend
pytest tests/ -v                    # All tests
pytest tests/test_prompts.py::TestPromptCRUD -v  # Specific test class
pytest tests/test_prompts.py::TestVersioning::test_create_version -v  # Single test
pytest tests/ --cov=app            # With coverage
```

### View API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Reset Database
```bash
rm backend/test.db              # SQLite
psql -c "DROP DATABASE prompt_optimization;"  # PostgreSQL
```

### Check Database
```bash
# SQLite
sqlite3 backend/test.db ".tables"
sqlite3 backend/test.db "SELECT * FROM users;"

# PostgreSQL
psql prompt_optimization
\dt
SELECT * FROM users;
```

---

## 🔐 Authentication Flow

### 1. Register
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123",
    "full_name": "John Doe"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/api/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=securepass123"
```

Save the returned `access_token` as `TOKEN`

### 3. Use Token
```bash
curl http://localhost:8000/api/prompts/ \
  -H "Authorization: Bearer TOKEN"
```

---

## 📝 Prompt Operations

### Create Prompt
```bash
curl -X POST http://localhost:8000/api/prompts/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Prompt",
    "description": "A useful prompt",
    "content": "You are a helpful assistant...",
    "model": "gpt-3.5-turbo",
    "tags": ["tag1", "tag2"]
  }'
```

### List Prompts
```bash
curl http://localhost:8000/api/prompts/ \
  -H "Authorization: Bearer TOKEN"

# With pagination
curl "http://localhost:8000/api/prompts/?skip=0&limit=5" \
  -H "Authorization: Bearer TOKEN"
```

### Get Prompt
```bash
curl http://localhost:8000/api/prompts/1 \
  -H "Authorization: Bearer TOKEN"
```

### Update Prompt
```bash
curl -X PUT http://localhost:8000/api/prompts/1 \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title"}'
```

### Delete Prompt
```bash
curl -X DELETE http://localhost:8000/api/prompts/1 \
  -H "Authorization: Bearer TOKEN"
```

---

## 📚 Version Operations

### Create Version
```bash
curl -X POST http://localhost:8000/api/prompts/1/versions \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Updated content...",
    "model": "gpt-4",
    "change_description": "Improved clarity"
  }'
```

### List Versions
```bash
curl http://localhost:8000/api/prompts/1/versions \
  -H "Authorization: Bearer TOKEN"
```

### Compare Versions
```bash
curl -X POST "http://localhost:8000/api/prompts/1/compare?version_1_id=1&version_2_id=2" \
  -H "Authorization: Bearer TOKEN"
```

### Rollback Version
```bash
curl -X POST http://localhost:8000/api/prompts/1/rollback/1 \
  -H "Authorization: Bearer TOKEN"
```

---

## 🧪 Testing Examples

### Run All Tests
```bash
pytest backend/tests/ -v
```

### Run with Coverage Report
```bash
pytest backend/tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

### Run Specific Test
```bash
pytest backend/tests/test_prompts.py::TestPromptCRUD::test_create_prompt -v
```

### Generate Test Database
Tests automatically create isolated database.

---

## 🔧 Configuration

### Backend (.env)
```env
# Database
DATABASE_URL=sqlite:///./test.db
# or
DATABASE_URL=postgresql://user:password@localhost/prompt_optimization

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Frontend (app.js)
```javascript
const API_BASE_URL = "http://localhost:8000/api";
```

---

## 📁 File Organization

```
backend/
  app/
    main.py           # FastAPI app entry point
    models.py         # Database models
    schemas.py        # Request/response models
    auth.py           # Auth utilities
    routes/
      auth.py         # Auth endpoints
      prompts.py      # Prompt endpoints
  tests/
    test_prompts.py   # All tests
  requirements.txt    # Dependencies

frontend/
  index.html          # UI
  app.js              # JavaScript logic
```

---

## 🐛 Debugging

### Backend Debug Mode
```python
# In app/main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### View Logs
```bash
# Backend logs appear in terminal when using --reload
# Look for [INFO], [WARNING], [ERROR] messages

# Database queries (SQLAlchemy)
# Enable with logging config
```

### Test a Single Endpoint
```bash
# Use http://localhost:8000/docs to test interactively
# Or use curl with verbose flag
curl -v http://localhost:8000/api/prompts/ \
  -H "Authorization: Bearer TOKEN"
```

---

## 📊 Database Inspection

### View All Tables
```bash
# SQLite
sqlite3 backend/test.db ".tables"

# PostgreSQL
psql prompt_optimization -c "\dt"
```

### Check Table Schema
```bash
# SQLite
sqlite3 backend/test.db ".schema users"

# PostgreSQL
psql prompt_optimization -c "\d users"
```

### Query Data
```bash
# SQLite
sqlite3 backend/test.db "SELECT * FROM prompts LIMIT 10;"

# PostgreSQL
psql prompt_optimization -c "SELECT * FROM prompts LIMIT 10;"
```

---

## 🐳 Docker Operations

### Build Image
```bash
docker build -t prompt-optimization .
```

### Run with Docker Compose
```bash
docker-compose up -d
docker-compose logs -f
docker-compose down
```

### Access Running Container
```bash
docker exec -it prompt_optimization_api bash
```

---

## ✅ Development Checklist

- [ ] Backend running on 8000
- [ ] Frontend running on 8001
- [ ] Can register new user
- [ ] Can login and get token
- [ ] Can create prompt
- [ ] Can create version
- [ ] Can compare versions
- [ ] Can rollback version
- [ ] All tests passing

---

## 🚨 Troubleshooting

### Port Already in Use
```bash
# Find process
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

### Database Connection Error
```bash
# SQLite - remove and recreate
rm backend/test.db

# PostgreSQL - check service
pg_isready -h localhost
psql -U postgres
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### CORS Error
- Check frontend is running on correct port
- Check API_BASE_URL in app.js
- Ensure backend is on port 8000

---

## 📖 Documentation Map

| Document | Content | Read Time |
|----------|---------|-----------|
| README.md | Overview, features, setup | 5 min |
| SETUP_GUIDE.md | Detailed setup & troubleshooting | 10 min |
| API_SPEC.md | Complete API reference | 15 min |
| IMPLEMENTATION_SUMMARY.md | What was built | 10 min |
| QUICK_REFERENCE.md | This file - commands & tasks | 5 min |

---

## 🔗 Useful Links

### Local Services
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Frontend: http://localhost:8001
- Health Check: http://localhost:8000/health

### External Resources
- FastAPI: https://fastapi.tiangolo.com/
- SQLAlchemy: https://docs.sqlalchemy.org/
- Pydantic: https://docs.pydantic.dev/
- JWT: https://jwt.io/

---

## ⚡ Quick Commands

```bash
# Setup
cd backend && pip install -r requirements.txt

# Run
uvicorn app.main:app --reload

# Test
pytest tests/ -v

# Database reset
rm test.db

# View docs
http://localhost:8000/docs

# Frontend dev
python -m http.server 8001
```

---

## 🎯 Quick Test Workflow

```bash
# 1. Start backend
cd backend && uvicorn app.main:app --reload

# 2. In another terminal, run tests
cd backend && pytest tests/ -v

# 3. Open browser to frontend
cd frontend && python -m http.server 8001

# 4. Test in UI
# - Register new account
# - Create prompt
# - Create version
# - View history
# - Compare versions
```

---

## 💡 Pro Tips

1. **Use Swagger UI** for testing endpoints interactively
2. **Check logs** in terminal where backend is running
3. **Save token** from login response for curl commands
4. **Use ReDoc** for better API documentation reading
5. **Run tests often** to catch breaking changes
6. **Check database** with SQLite browser for local development

---

**Need more help?** Check the full documentation in README.md or API_SPEC.md
