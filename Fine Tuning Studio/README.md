# Fine-Tuning Studio

A comprehensive platform for training and fine-tuning large language models (LLMs) with support for multiple architectures and advanced training techniques.

## 📋 Features

### Core Capabilities
- **LoRA** - Low-Rank Adaptation for efficient fine-tuning
- **QLoRA** - Quantized LoRA for memory-efficient training
- **PEFT** - Parameter-Efficient Fine-Tuning methods
- **Dataset Builder** - Upload and manage datasets
- **Training Dashboard** - Real-time training metrics
- **Checkpoint Management** - Save and restore model checkpoints
- **Model Comparison** - Compare multiple trained models
- **Merge Adapters** - Merge adapters to base models

### Supported Models
- Llama (7B, 13B, 70B)
- Mistral (7B)
- Qwen (7B, 14B)

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional)
- CUDA 11.8+ (for GPU support)

### Local Development Setup

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

#### Frontend Setup
```bash
cd frontend
npm install
npm start
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- API Docs: http://localhost:5000/api/docs

### Docker Setup

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database
- Redis cache
- Backend API (port 5000)
- Frontend (port 3000)

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Flask Configuration
FLASK_ENV=development
DEBUG=True
PORT=5000

# Database
DATABASE_URL=postgresql://user:password@localhost/finetuning_studio

# JWT
JWT_SECRET_KEY=your-secret-key-here

# Redis
REDIS_URL=redis://localhost:6379/0

# Model Configuration
USE_GPU=true
MODEL_CACHE_DIR=./models_cache

# Logging
LOG_LEVEL=INFO
```

## 📚 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/create-api-key` - Create API key
- `GET /api/auth/api-keys` - List API keys
- `DELETE /api/auth/api-keys/<key_id>` - Delete API key

### Models
- `GET /api/models/supported` - Get supported model types
- `GET /api/models` - List available models
- `GET /api/models/<id>` - Get model details
- `POST /api/models` - Register new model
- `PUT /api/models/<id>` - Update model
- `DELETE /api/models/<id>` - Delete model

### Health
- `GET /api/health` - Health check
- `GET /api/ping` - Ping

## 🏗️ Project Structure

```
Fine Tuning Studio/
├── backend/
│   ├── app/
│   │   ├── config.py           # Configuration
│   │   ├── logger.py           # Logging setup
│   │   ├── models/             # Database models
│   │   ├── routes/             # API routes
│   │   ├── middleware/         # Error handling
│   │   └── utils/              # Utilities
│   ├── tests/                  # Unit tests
│   ├── requirements.txt        # Python dependencies
│   └── run.py                  # Entry point
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── pages/              # Page components
│   │   ├── services/           # API services
│   │   ├── store/              # Redux store
│   │   └── styles/             # CSS styles
│   └── package.json            # NPM dependencies
├── docker-compose.yml          # Docker setup
└── plan.md                     # Development plan
```

## 🔐 Security

- JWT-based authentication
- API key support for programmatic access
- Role-based access control (RBAC)
- Password hashing with bcrypt
- CORS configuration
- Input validation and error handling

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📊 Database Schema

### Users
- id, username, email, password_hash, role, is_active, created_at, updated_at

### API Keys
- id, user_id, key, name, is_active, last_used_at, created_at, updated_at

### Models
- id, name, model_type, model_size, huggingface_id, description, parameters_count, context_window, is_active

### Datasets
- id, name, user_id, file_path, file_format, total_samples, status, metadata

### Training Jobs
- id, name, user_id, model_id, dataset_id, training_type, status, progress, output_dir

### Checkpoints
- id, training_job_id, checkpoint_name, step, loss, accuracy, checkpoint_path, is_best

## 📈 Development Roadmap

See [plan.md](./plan.md) for the complete 4-phase development plan.

### Phase 1 (Current): Core Infrastructure ✅
- Project structure
- Model support foundation
- Authentication & authorization
- Database setup
- API foundation

### Phase 2: Dataset & Training
- Dataset builder
- Training pipelines
- Checkpoint management
- Model quantization

### Phase 3: Dashboard & Monitoring
- Training dashboard
- Metrics collection
- Model comparison
- Inference testing

### Phase 4: Advanced Features
- Merge adapters
- Model export
- Distributed training
- Production deployment

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Write tests
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For issues and questions, please create an issue on GitHub or contact the development team.

## 📞 Contact

- Email: support@finetuning-studio.com
- Slack: #finetuning-studio-dev
