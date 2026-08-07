# Fine-Tuning Studio

A comprehensive, production-ready platform for training and fine-tuning large language models (LLMs) with support for multiple architectures, parameter-efficient methods, and advanced training techniques.

## Overview

Fine-Tuning Studio provides an end-to-end solution for adapting pre-trained LLMs to specific tasks and domains. Whether you're looking for quick prototyping or production-scale fine-tuning, this platform offers flexible, efficient training options with minimal computational overhead.

## 🎯 Key Features

### Parameter-Efficient Fine-Tuning Methods
- **LoRA** — Low-Rank Adaptation for efficient fine-tuning with minimal parameter overhead
- **QLoRA** — Quantized LoRA for memory-efficient training on consumer-grade GPUs
- **PEFT** — Parameter-Efficient Fine-Tuning framework with multiple adapter strategies

### Dataset & Training Management
- **Dataset Builder** — Upload, validate, and manage training datasets in multiple formats
- **Training Dashboard** — Real-time monitoring of training metrics and progress
- **Checkpoint Management** — Automatic checkpoint saving, restoration, and best-model selection
- **Multi-Model Support** — Train on multiple model architectures simultaneously

### Analysis & Optimization
- **Model Comparison** — Compare performance across different fine-tuned versions
- **Adapter Merging** — Merge adapter weights back into base models for deployment
- **Performance Metrics** — Comprehensive evaluation and logging of training progress

### Supported Model Families
- **Llama** — 7B, 13B, 70B variants
- **Mistral** — 7B base and instruct models
- **Qwen** — 7B, 14B, and larger variants

## 🚀 Quick Start

### System Requirements
- **Python** 3.11 or higher
- **Node.js** 18+ (for frontend)
- **CUDA** 11.8+ (optional, for GPU acceleration)
- **RAM** Minimum 16GB (32GB recommended for large models)
- **Storage** At least 100GB for model storage

### Installation

#### 1. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your configuration
```

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm start
```

#### 3. Start Services
Once both backend and frontend are configured:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **API Documentation**: http://localhost:5000/api/docs (Swagger UI)

### Docker Deployment

For containerized deployment with all services:

```bash
docker-compose up -d
```

This starts:
- PostgreSQL database (persistent storage)
- Redis cache (session management)
- Backend API (FastAPI on port 5000)
- Frontend (React on port 3000)

Monitor containers:
```bash
docker-compose logs -f
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory with the following configuration:

```env
# Application
ENVIRONMENT=development        # development | production | staging
DEBUG=True
SECRET_KEY=your-secret-key-change-in-production

# Server
PORT=5000
HOST=0.0.0.0

# Database
DATABASE_URL=postgresql://user:password@localhost/finetuning_studio
# For SQLite (development only):
# DATABASE_URL=sqlite:///./finetuning.db

# Cache & Sessions
REDIS_URL=redis://localhost:6379/0

# Security
JWT_SECRET_KEY=your-secure-jwt-secret-key
JWT_EXPIRATION_HOURS=24

# Model Configuration
USE_GPU=true
MODEL_CACHE_DIR=./models_cache
MAX_MODEL_SIZE_GB=100
CUDA_DEVICE_ID=0

# Training
DEFAULT_LEARNING_RATE=1e-4
BATCH_SIZE=4
MAX_EPOCHS=3

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
```

### Model Configuration

Configure supported models in `backend/config/models.yaml`:

```yaml
models:
  - name: llama-7b
    path: /models/llama-7b-hf
    adapter_type: lora
    default_rank: 8
    
  - name: mistral-7b
    path: /models/mistral-7b-instruct
    adapter_type: lora
    default_rank: 16
```

## 📚 Core API Endpoints

### Authentication
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | Create new user account |
| `/api/auth/login` | POST | Authenticate and receive JWT token |
| `/api/auth/me` | GET | Get current user profile |
| `/api/auth/create-api-key` | POST | Generate programmatic API key |
| `/api/auth/api-keys` | GET | List all API keys |
| `/api/auth/api-keys/<key_id>` | DELETE | Revoke API key |

### Model Management
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/models/supported` | GET | List supported base models |
| `/api/models` | GET | List available models |
| `/api/models/<id>` | GET | Get model details and metadata |
| `/api/models` | POST | Register new base model |
| `/api/models/<id>` | PUT | Update model configuration |
| `/api/models/<id>` | DELETE | Remove model |

### Training Jobs
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/training/jobs` | GET | List all training jobs |
| `/api/training/jobs` | POST | Create new training job |
| `/api/training/jobs/<job_id>` | GET | Get job status and metrics |
| `/api/training/jobs/<job_id>/stop` | POST | Stop running job |
| `/api/training/jobs/<job_id>/checkpoints` | GET | List job checkpoints |

### System
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | System health status |
| `/api/metrics` | GET | Training metrics and statistics |

## 📁 Project Structure

```
Fine Tuning Studio/
├── backend/                      # FastAPI application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI application entry
│   │   ├── config.py           # Configuration management
│   │   ├── logger.py           # Logging configuration
│   │   ├── models/             # SQLAlchemy ORM models
│   │   │   ├── user.py
│   │   │   ├── model.py
│   │   │   ├── training_job.py
│   │   │   └── checkpoint.py
│   │   ├── routes/             # API endpoint handlers
│   │   │   ├── auth.py
│   │   │   ├── models.py
│   │   │   └── training.py
│   │   ├── schemas/            # Pydantic request/response models
│   │   ├── middleware/         # CORS, auth, error handling
│   │   ├── services/           # Business logic layer
│   │   │   ├── trainer.py
│   │   │   └── model_service.py
│   │   └── utils/              # Helper functions
│   ├── tests/                  # Pytest test suite
│   │   ├── test_auth.py
│   │   ├── test_models.py
│   │   └── test_training.py
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example            # Environment template
│   └── run.py                  # Development server script
│
├── frontend/                     # React single-page application
│   ├── public/
│   ├── src/
│   │   ├── components/         # Reusable React components
│   │   │   ├── Dashboard/
│   │   │   ├── TrainingForm/
│   │   │   └── ModelSelector/
│   │   ├── pages/              # Full page components
│   │   │   ├── Home.jsx
│   │   │   ├── Training.jsx
│   │   │   └── Results.jsx
│   │   ├── services/           # API client functions
│   │   ├── store/              # Redux state management
│   │   ├── styles/             # CSS/SCSS
│   │   ├── App.jsx
│   │   └── index.jsx
│   ├── package.json            # NPM dependencies
│   └── .env.example
│
├── docker-compose.yml          # Multi-container orchestration
├── Dockerfile                  # Container image definition
├── .dockerignore
├── .gitignore
├── plan.md                     # Development roadmap
└── README.md                   # This file
```

## 🔐 Security

### Authentication & Authorization
- ✅ JWT (JSON Web Token) based authentication
- ✅ Bcrypt password hashing with salt
- ✅ API key support for programmatic access
- ✅ Role-based access control (RBAC) — user, admin, superuser roles
- ✅ Session management with Redis
- ✅ Refresh token rotation

### Data Protection
- ✅ CORS configuration for cross-origin requests
- ✅ SQL injection prevention via SQLAlchemy ORM
- ✅ Request input validation and sanitization
- ✅ Rate limiting on sensitive endpoints
- ✅ Encrypted storage for API keys

### Deployment Security
- ✅ HTTPS enforcement in production
- ✅ Environment-based secret management
- ✅ Docker image scanning for vulnerabilities
- ✅ Database connection pooling and timeouts

## 🧪 Testing

### Running Backend Tests
```bash
cd backend

# All tests
pytest tests/ -v

# With coverage report
pytest tests/ --cov=app --cov-report=html

# Specific test file
pytest tests/test_auth.py -v
```

### Running Frontend Tests
```bash
cd frontend

# Run all tests
npm test

# Watch mode
npm test -- --watch

# Coverage report
npm test -- --coverage
```

### Test Categories
- **Unit Tests** — Individual function and class testing
- **Integration Tests** — API endpoint and database interaction
- **E2E Tests** — Full workflow testing from UI to database

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(255) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  full_name VARCHAR(255),
  role VARCHAR(50) DEFAULT 'user',  -- user, admin, superuser
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  last_login TIMESTAMP
);
```

### API Keys Table
```sql
CREATE TABLE api_keys (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  key VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  last_used_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  expires_at TIMESTAMP
);
```

### Models Table
```sql
CREATE TABLE models (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  model_type VARCHAR(100),  -- llama, mistral, qwen
  model_size VARCHAR(20),   -- 7b, 13b, 70b
  huggingface_id VARCHAR(255),
  description TEXT,
  parameters_count BIGINT,
  context_window INTEGER DEFAULT 4096,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Training Jobs Table
```sql
CREATE TABLE training_jobs (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  user_id INTEGER REFERENCES users(id),
  model_id INTEGER REFERENCES models(id),
  dataset_id INTEGER,
  training_type VARCHAR(50),  -- lora, qlora, peft
  status VARCHAR(50),         -- pending, running, completed, failed
  progress FLOAT DEFAULT 0,
  loss FLOAT,
  output_dir VARCHAR(255),
  created_at TIMESTAMP DEFAULT NOW(),
  started_at TIMESTAMP,
  completed_at TIMESTAMP
);
```

### Checkpoints Table
```sql
CREATE TABLE checkpoints (
  id SERIAL PRIMARY KEY,
  training_job_id INTEGER REFERENCES training_jobs(id) ON DELETE CASCADE,
  checkpoint_name VARCHAR(255),
  step INTEGER,
  loss FLOAT,
  accuracy FLOAT,
  checkpoint_path VARCHAR(255),
  is_best BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
);
```

## 📈 Development Roadmap

For the complete 4-phase development strategy, see [plan.md](./plan.md).

### Phase 1: Core Infrastructure ✅
- [x] Project structure and scaffolding
- [x] Model support foundation
- [x] User authentication & authorization system
- [x] Database schema and migrations
- [x] RESTful API foundation
- [x] Docker containerization
- [x] Unit test framework

### Phase 2: Dataset & Training (In Progress)
- [ ] Dataset upload and validation
- [ ] Dataset preprocessing pipeline
- [ ] LoRA training implementation
- [ ] QLoRA training implementation
- [ ] Training job queuing and scheduling
- [ ] Checkpoint auto-saving
- [ ] Model quantization support

### Phase 3: Dashboard & Monitoring
- [ ] Real-time training dashboard
- [ ] Metrics collection and visualization
- [ ] Model comparison tool
- [ ] Inference testing interface
- [ ] Training history and analytics
- [ ] Performance metrics export

### Phase 4: Advanced Features & Production
- [ ] Multi-GPU training support
- [ ] Distributed training
- [ ] Adapter merging and export
- [ ] Model quantization and optimization
- [ ] Inference optimization
- [ ] Production deployment guides
- [ ] Performance benchmarking
- [ ] Load testing and scaling

## 🤝 Contributing

We welcome contributions from the community! Here's how to get involved:

### Development Workflow
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes with clear, descriptive commits
4. Add tests for new functionality
5. Ensure all tests pass: `pytest tests/`
6. Submit a pull request with a detailed description

### Coding Standards
- Follow PEP 8 for Python code
- Use type hints for function signatures
- Write docstrings for classes and complex functions
- Maintain test coverage above 80%
- Format code with `black` and check with `flake8`

### Reporting Issues
When reporting bugs, please include:
- Clear description of the issue
- Steps to reproduce
- Expected vs. actual behavior
- Environment details (OS, Python version, CUDA version)
- Relevant logs or error messages

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 💬 Getting Help

### Documentation
- Check [plan.md](./plan.md) for development roadmap
- Review API documentation at `/api/docs` when server is running
- Explore example scripts in the `examples/` directory

### Community Support
- **GitHub Issues** — For bug reports and feature requests
- **Discussions** — For general questions and ideas
- **Email** — support@finetuning-studio.com
- **Slack** — Join us at #finetuning-studio-dev

### Troubleshooting
- See the [Troubleshooting Guide](#troubleshooting) section
- Check common issues in [GitHub Discussions](https://github.com/yourusername/fine-tuning-studio/discussions)
- Review backend logs: `tail -f logs/app.log`

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) — Modern Python web framework
- [React](https://react.dev/) — UI library
- [PyTorch](https://pytorch.org/) — Deep learning framework
- [Hugging Face Transformers](https://huggingface.co/transformers/) — Model library
- [PEFT](https://github.com/huggingface/peft) — Parameter-efficient fine-tuning
