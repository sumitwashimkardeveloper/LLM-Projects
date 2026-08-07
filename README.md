# LLM Ecosystem Platform

A **comprehensive, production-ready ecosystem** for working with large language models. This monorepo contains four interconnected projects that cover the complete LLM lifecycle: **inference, evaluation, fine-tuning, and prompt optimization**.

## 🎯 Project Overview

This platform provides everything you need to deploy, evaluate, fine-tune, and optimize LLMs at scale:

| Project | Purpose | Status |
|---------|---------|--------|
| **LLM Inference Engine** | Self-hosted, OpenAI-API-compatible inference server | ✅ Phase 4 (Production) |
| **LLM Evaluation Framework** | Comprehensive model evaluation and benchmarking | ✅ Complete |
| **Fine Tuning Studio** | Platform for fine-tuning LLMs with PEFT methods | 🟡 Phase 1-2 |
| **Prompt Optimization** | Version control and optimization for prompts | ✅ Phase 1 |

## 📁 Quick Navigation

```
LLM Ecosystem/
├── LLM Inference Engine/          # Run models locally
│   └── README.md
├── LLM Evaluation Framework/      # Compare and evaluate models
│   └── README.md
├── Fine Tuning Studio/            # Fine-tune models
│   └── README.md
├── Prompt Optimisation/           # Manage and optimize prompts
│   └── README.md
└── README.md                      # This file
```

## 🚀 Getting Started

### Quick Start (Choose Your Path)

**Option 1: Just Run a Model Locally**
```bash
cd "LLM Inference Engine"
# See README.md for setup
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Option 2: Compare Multiple Models**
```bash
cd "LLM Eval"
# See README.md for setup
python -m pip install -r requirements.txt
python quick_start.py
```

**Option 3: Fine-Tune a Model**
```bash
cd "Fine Tuning Studio/backend"
# See README.md for setup
python -m pip install -r requirements.txt
python run.py
```

**Option 4: Manage Your Prompts**
```bash
cd "Prompt Optimisation/backend"
# See README.md for setup
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 🔗 Project Descriptions

### 1. 🏃 LLM Inference Engine

**Self-hosted inference server with OpenAI-API compatibility**

Run quantized LLMs locally without cloud dependencies. Multi-backend support (GGUF for CPU, AWQ for GPU) with continuous batching, rate limiting, and comprehensive monitoring.

**Key Features:**
- OpenAI API v1 compatible endpoints
- Multi-model management with slot pooling
- GGUF (llama.cpp) and AWQ backends
- Prometheus metrics and structured logging
- API key authentication and rate limiting
- Docker containerization included

**Best For:**
- Running models on your own infrastructure
- Privacy-sensitive workloads
- Cost optimization at scale
- Custom deployment requirements

**[See Full Documentation →](./LLM%20Inference%20Engine/README.md)**

---

### 2. 📊 LLM Evaluation Framework

**Comprehensive framework for evaluating and comparing LLMs**

Systematically evaluate models across accuracy, cost, latency, and quality metrics. Compare models with arena tournaments, run benchmarks, and make data-driven decisions.

**Key Features:**
- 8+ evaluation metrics (BLEU, ROUGE, BERTScore, hallucination detection)
- Multi-provider support (Claude, GPT, Gemini, Llama)
- Arena tournament and head-to-head comparison
- Comprehensive benchmarking (latency, cost, quality, throughput)
- Statistical analysis and reporting
- Result caching and export (JSON, CSV, HTML)

**Best For:**
- Selecting the best model for your use case
- Benchmarking model performance
- Cost-benefit analysis
- Quality assurance
- Creating comprehensive evaluation reports

**[See Full Documentation →](./LLM%20Eval/README.md)**

---

### 3. 🎓 Fine Tuning Studio

**Production-grade platform for fine-tuning LLMs**

Efficiently fine-tune models using parameter-efficient methods (LoRA, QLoRA, PEFT). Full training pipeline with checkpoint management, dashboard monitoring, and adapter merging.

**Key Features:**
- LoRA, QLoRA, PEFT support
- Multi-model architecture support
- Real-time training dashboard
- Checkpoint auto-save and best-model selection
- Adapter merging for deployment
- Comprehensive model comparison

**Best For:**
- Domain-specific model adaptation
- Cost-effective fine-tuning
- Production model customization
- Multi-user team collaboration
- Experimental model iteration

**[See Full Documentation →](./Fine%20Tuning%20Studio/README.md)**

---

### 4. ✨ Prompt Optimization Platform

**Version control and optimization for LLM prompts**

Manage prompts like code with complete version history, comparison, and rollback. Track performance metrics and systematically optimize prompt performance.

**Key Features:**
- Prompt version control and history
- Side-by-side version comparison
- One-click rollback to any version
- Metadata and performance tracking
- Team collaboration with access control
- A/B testing framework (Phase 2)
- Automatic optimization tools (Phase 3+)

**Best For:**
- Prompt versioning and collaboration
- Testing prompt variations
- Performance tracking
- Team workflow management
- Experimentation and iteration

**[See Full Documentation →](./Prompt%20Optimisation/README.md)**

---

## 🔄 Typical Workflows

### Workflow 1: Evaluate Models & Deploy the Best One
```
1. Use LLM Evaluation Framework to benchmark models
2. Choose the best model for your requirements
3. Deploy with LLM Inference Engine
4. Monitor performance with integrated metrics
```

### Workflow 2: Fine-Tune & Optimize for Your Domain
```
1. Start with a base model
2. Fine-tune with Fine Tuning Studio
3. Evaluate with LLM Evaluation Framework
4. Deploy optimized model with Inference Engine
```

### Workflow 3: Iteratively Improve Your Prompts
```
1. Create prompts in Prompt Optimization
2. Test versions with different models
3. Track performance metrics
4. Use Evaluation Framework to measure quality
5. Merge winning prompts back to production
```

### Workflow 4: Complete Production Pipeline
```
1. Find/fine-tune best model (Eval + Fine-Tuning)
2. Deploy model locally (Inference Engine)
3. Manage prompts and versions (Prompt Optimization)
4. Continuously monitor and optimize
5. A/B test improvements (Prompt Optimization Phase 2)
```

## 🛠️ Technology Stack

### Backend
- **Python 3.10+** — Primary language
- **FastAPI** — Modern async web framework
- **SQLAlchemy** — Database ORM
- **PyTorch** — Deep learning framework
- **llama.cpp** — Efficient CPU/GPU inference
- **Hugging Face Transformers** — Model library
- **PEFT** — Parameter-efficient fine-tuning

### Frontend
- **React/Vanilla JavaScript** — Web UI
- **CSS3** — Responsive styling
- **Fetch API** — HTTP communication

### Infrastructure
- **Docker** — Containerization
- **PostgreSQL** — Production database
- **Redis** — Caching and sessions
- **Prometheus** — Metrics collection

### Testing & Quality
- **pytest** — Unit testing
- **Coverage** — Code coverage analysis
- **GitHub Actions** — CI/CD

## 📋 System Requirements

### Minimum (Development)
- Python 3.10+
- 8GB RAM
- 50GB disk space
- CPU with 4+ cores

### Recommended (Production)
- Python 3.10+
- 32GB+ RAM (for multiple models)
- 200GB+ disk space (for multiple model files)
- NVIDIA GPU with 8GB+ VRAM (optional, for faster inference)
- Dedicated inference GPU (A100, H100 for production)

## 🚀 Installation & Setup

### Prerequisites
- Git
- Python 3.10+
- Docker & Docker Compose (optional)

### Standard Setup (All Components)

```bash
# Clone the repository
git clone <repository-url>
cd LLM

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Install project dependencies
pip install -e .
```

### Individual Project Setup

Each sub-project can be set up independently. See the project-specific README files:

- [LLM Inference Engine Setup](./LLM%20Inference%20Engine/README.md#installation)
- [LLM Evaluation Setup](./LLM%20Eval/README.md#installation)
- [Fine Tuning Studio Setup](./Fine%20Tuning%20Studio/README.md#installation)
- [Prompt Optimization Setup](./Prompt%20Optimisation/README.md#installation)

## 🐳 Docker Deployment

### All Services with Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📊 Architecture

```
┌─────────────────────────────────────────────────────┐
│                   User Applications                 │
└─────────────┬───────────────────────────────────┬───┘
              │                                   │
      ┌───────▼────────┐             ┌───────────▼──────┐
      │  Web Dashboard │             │   API Clients    │
      └───────┬────────┘             └───────┬──────────┘
              │                              │
      ┌───────▼──────────────────────────────▼──────────┐
      │           API Gateway / Router                  │
      └───┬──────────────┬──────────────┬──────────────┬┘
          │              │              │              │
     ┌────▼────┐  ┌─────▼──────┐ ┌────▼────┐  ┌─────▼──┐
     │Inference│  │  Evaluation│ │Fine-tune│  │ Prompt │
     │ Engine  │  │ Framework  │ │ Studio  │  │Optimize│
     └────┬────┘  └─────┬──────┘ └────┬────┘  └──┬─────┘
          │             │             │          │
     ┌────▼─────────────▼─────────────▼──────────▼─────┐
     │           Model Repository / Storage            │
     └────┬─────────────────────────────────────────────┘
          │
     ┌────▼──────────────────────────┐
     │    Database (PostgreSQL)       │
     │    Cache (Redis)               │
     │    File Storage                │
     └───────────────────────────────┘
```

## 📈 Performance Metrics

### Inference Engine
- **Throughput**: 5-100 tokens/sec (varies by model and hardware)
- **Latency**: 100-500ms first token (TTFT)
- **Concurrent Requests**: 2-16 per model (configurable)
- **Memory Per Model**: 4-70GB (depends on model size and quantization)

### Evaluation Framework
- **Evaluation Time**: 0.5-2 seconds per prompt (varies by metrics)
- **Batch Processing**: 10-100 prompts in parallel
- **Report Generation**: <5 seconds for 100 prompts

### Fine-Tuning Studio
- **Training Speed**: 50-200 tokens/sec (with GPU)
- **Memory Efficiency**: 2-8GB for LoRA (vs 24GB+ for full fine-tuning)
- **Checkpoint Size**: 50MB-2GB (depends on model and adapter type)

## 🔐 Security

### Built-in Protections
- ✅ JWT-based authentication
- ✅ API key management
- ✅ CORS configuration
- ✅ Rate limiting
- ✅ Input validation
- ✅ SQL injection prevention (ORM)
- ✅ Password hashing (bcrypt)

### Deployment Security
- ✅ Environment-based secrets management
- ✅ TLS/HTTPS support
- ✅ Database connection pooling
- ✅ Container security scanning
- ✅ Audit logging (optional)

## 📚 Documentation

### Project Documentation
- [LLM Inference Engine](./LLM%20Inference%20Engine/README.md)
- [LLM Evaluation Framework](./LLM%20Eval/README.md)
- [Fine Tuning Studio](./Fine%20Tuning%20Studio/README.md)
- [Prompt Optimization](./Prompt%20Optimisation/README.md)

### Development
- See `plan.md` in each project for detailed development roadmaps
- API documentation available at `/docs` when servers are running

## 🧪 Testing

Run all tests across projects:

```bash
# Inference Engine tests
cd LLM\ Inference\ Engine
pytest tests/ -v

# Evaluation Framework tests
cd LLM\ Eval
python test_framework.py

# Fine Tuning tests
cd Fine\ Tuning\ Studio/backend
pytest tests/ -v

# Prompt Optimization tests
cd Prompt\ Optimisation/backend
pytest tests/ -v --cov=app
```

## 🤝 Contributing

We welcome contributions from the community! Here's how:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Make** your changes with clear commits
4. **Test** your changes thoroughly
5. **Submit** a pull request

### Guidelines
- Follow project coding standards (PEP 8 for Python)
- Write tests for new features
- Update documentation as needed
- Keep commits atomic and descriptive
- Ensure all tests pass before submitting PR

## 📝 License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) file for details.

Each sub-project maintains its own license file.

## 🐛 Issue Tracking

Found a bug or have a feature request?
- **GitHub Issues** — Report issues with reproduction steps
- **GitHub Discussions** — Ask questions and share ideas
- **Pull Requests** — Submit contributions with context

## 💬 Community & Support

### Getting Help
- **Documentation** — Read project READMEs and plan.md files
- **Examples** — Check examples.py and quick_start.py in each project
- **API Docs** — Interactive Swagger UI at `/docs` endpoints
- **Community** — GitHub Discussions and Issues

### Contact
- **Email** — support@llm-ecosystem.com (placeholder)
- **Slack** — #llm-ecosystem-dev (placeholder)
- **Twitter** — @LLMEcosystem (placeholder)

## 🗺️ Roadmap

### Near Term (3-6 months)
- [ ] Complete Fine Tuning Studio Phase 2
- [ ] Add A/B testing to Prompt Optimization
- [ ] Multi-GPU inference support
- [ ] Advanced analytics dashboard

### Mid Term (6-12 months)
- [ ] Model marketplace
- [ ] Advanced prompt optimization
- [ ] Cost optimization tools
- [ ] Performance prediction

### Long Term (12+ months)
- [ ] Distributed training
- [ ] Custom CUDA kernels
- [ ] Real-time prompt monitoring
- [ ] Automated model selection

## 🙏 Acknowledgments

This ecosystem stands on the shoulders of amazing open-source projects:

- [FastAPI](https://fastapi.tiangolo.com/) — Web framework
- [PyTorch](https://pytorch.org/) — Deep learning
- [llama.cpp](https://github.com/ggerganov/llama.cpp) — CPU inference
- [Hugging Face](https://huggingface.co/) — Model hub
- [PEFT](https://github.com/huggingface/peft) — Efficient fine-tuning
- [SQLAlchemy](https://www.sqlalchemy.org/) — Database ORM
- [Pydantic](https://docs.pydantic.dev/) — Data validation

## 📊 Key Stats

- **4** integrated projects
- **8+** evaluation metrics
- **4+** supported model providers
- **3** fine-tuning methods
- **100%** test coverage target
- **Production-ready** code

---

**Ready to work with LLMs at scale? Start with any project above and integrate them into your workflow!**

**Questions?** Check the individual project READMEs or open an issue.
