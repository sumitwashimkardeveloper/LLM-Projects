# Fine-Tuning Studio - Deployment Guide

## Prerequisites

- Docker & Docker Compose
- Kubernetes cluster (optional)
- PostgreSQL 13+
- Redis 6+
- Python 3.11+
- 8GB+ RAM, NVIDIA GPU recommended

## Development Deployment

```bash
cd Fine\ Tuning\ Studio
docker-compose up -d
```

Access:
- API: http://localhost:5000
- Frontend: http://localhost:3000

## Production Deployment

### Environment Setup

Create `.env.prod`:
```
FLASK_ENV=production
DATABASE_URL=postgresql://user:password@prod-db:5432/finetuning_studio
REDIS_URL=redis://:password@prod-redis:6379/0
JWT_SECRET_KEY=your-secret-key-here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
```

### Docker Compose Production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes Deployment

1. Create namespace:
```bash
kubectl create namespace finetuning
```

2. Create secrets:
```bash
kubectl create secret generic finetuning-secrets \
  --from-literal=database-url='postgresql://...' \
  --from-literal=redis-url='redis://...' \
  --from-literal=jwt-secret='...' \
  -n finetuning
```

3. Deploy:
```bash
kubectl apply -f k8s/deployment.yaml
```

4. Monitor:
```bash
kubectl logs -f deployment/finetuning-studio-backend -n finetuning
```

## Database Setup

### Initialize Database

```bash
python backend/init_db.py
```

### Backup

```bash
pg_dump finetuning_studio > backup.sql
```

### Restore

```bash
psql finetuning_studio < backup.sql
```

## SSL/TLS Configuration

1. Obtain certificate (Let's Encrypt):
```bash
certbot certonly --standalone -d finetuning-studio.com
```

2. Configure nginx:
```nginx
server {
    listen 443 ssl;
    server_name finetuning-studio.com;
    ssl_certificate /etc/letsencrypt/live/finetuning-studio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/finetuning-studio.com/privkey.pem;
    
    location / {
        proxy_pass http://backend:5000;
    }
}
```

## Monitoring & Logging

### Application Logs
```bash
docker logs finetuning_backend
```

### Metrics
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

### Log Aggregation
```bash
docker logs -f finetuning_backend | grep ERROR
```

## Backup Strategy

- Daily database backups
- Weekly full system backups
- Monthly archive to cold storage

## Scaling

### Horizontal Scaling
```bash
docker-compose up -d --scale backend=3
```

### Load Balancing
Configure nginx upstream:
```nginx
upstream backend {
    server backend-1:5000;
    server backend-2:5000;
    server backend-3:5000;
}
```

## Maintenance

### Health Checks
```bash
curl http://localhost:5000/api/health
```

### Database Maintenance
```bash
VACUUM ANALYZE;
```

### Cache Cleanup
```bash
redis-cli FLUSHDB
```

## Troubleshooting

### Database Connection Error
```bash
docker exec finetuning_postgres psql -U finetuning -d finetuning_studio -c "SELECT 1"
```

### Redis Connection Error
```bash
docker exec finetuning_redis redis-cli ping
```

### API Not Responding
```bash
docker restart finetuning_backend
```

### High Memory Usage
```bash
docker stats
docker exec finetuning_backend python -m memory_profiler run.py
```

## Security Checklist

- [ ] Change default passwords
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Set up API rate limiting
- [ ] Enable logging and monitoring
- [ ] Regular security updates
- [ ] Backup encryption
- [ ] Database backups

## Upgrade Procedure

1. Backup database
2. Pull latest code
3. Run migrations
4. Test in staging
5. Deploy to production
6. Monitor logs

```bash
git pull origin main
python backend/init_db.py
docker-compose up -d --build
```

## Support & Documentation

- Docs: https://docs.finetuning-studio.com
- Issues: https://github.com/finetuning-studio/issues
- Community: https://discord.gg/finetuning-studio
