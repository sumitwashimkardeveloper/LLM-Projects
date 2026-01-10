# Fine-Tuning Studio API Documentation

## Overview

Fine-Tuning Studio provides a comprehensive REST API for training and managing LLM models.

Base URL: `https://api.finetuning-studio.com`

## Authentication

All endpoints require JWT authentication via `Authorization: Bearer <token>` header.

### Obtain Token
```
POST /api/auth/login
Content-Type: application/json

{
  "username": "user",
  "password": "password"
}
```

## Endpoints

### Authentication (5)
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/create-api-key
- GET /api/auth/api-keys
- DELETE /api/auth/api-keys/<id>

### Models (6)
- GET /api/models/supported
- GET /api/models
- GET /api/models/<id>
- POST /api/models
- PUT /api/models/<id>
- DELETE /api/models/<id>

### Datasets (6)
- POST /api/datasets
- GET /api/datasets
- GET /api/datasets/<id>
- GET /api/datasets/<id>/preview
- POST /api/datasets/<id>/split
- DELETE /api/datasets/<id>

### Training (10)
- POST /api/training/jobs
- GET /api/training/jobs
- GET /api/training/jobs/<id>
- POST /api/training/jobs/<id>/start
- POST /api/training/jobs/<id>/pause
- POST /api/training/jobs/<id>/cancel
- DELETE /api/training/jobs/<id>
- GET /api/training/checkpoints/<job_id>
- POST /api/training/checkpoints/<id>/restore
- GET /api/training/jobs/<id>/metrics

### Dashboard (7)
- GET /api/dashboard/overview
- GET /api/dashboard/jobs/<id>/metrics
- GET /api/dashboard/jobs/<id>/metrics/recent
- GET /api/dashboard/jobs/<id>/progress
- GET /api/dashboard/jobs/<id>/logs
- POST /api/dashboard/jobs/compare
- GET /api/dashboard/jobs/<id>/checkpoints/best

### Inference (4)
- POST /api/inference/test
- POST /api/inference/test/batch
- POST /api/inference/benchmark/<id>
- POST /api/inference/compare

### Alerts (4)
- GET /api/alerts
- POST /api/alerts/notify/completion
- POST /api/alerts/notify/resource
- POST /api/alerts/notify/error

### Export (4)
- POST /api/export/jobs/<id>/merge
- POST /api/export/jobs/<id>/export/huggingface
- POST /api/export/jobs/<id>/export/onnx
- POST /api/export/jobs/<id>/export/torchscript
- POST /api/export/jobs/<id>/export/ggml

### Collaboration (6)
- POST /api/collaboration/teams
- GET /api/collaboration/teams
- POST /api/collaboration/teams/<id>/members
- POST /api/collaboration/jobs/<id>/share
- POST /api/collaboration/jobs/<id>/comments
- GET /api/collaboration/jobs/<id>/comments
- POST /api/collaboration/config-versions
- GET /api/collaboration/config-versions

## Response Format

All responses use JSON format:

### Success Response
```json
{
  "data": {...},
  "status": 200
}
```

### Error Response
```json
{
  "error": "Error message",
  "status": 400
}
```

## Error Codes

- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 409: Conflict
- 500: Internal Server Error

## Rate Limiting

- 1000 requests per hour per user
- 100 concurrent requests per user

## Pagination

Endpoints supporting pagination use `limit` and `offset` parameters:
```
GET /api/resource?limit=10&offset=0
```

## Webhooks

Training job updates can be sent to webhooks:

```
POST /api/webhooks/register
{
  "url": "https://example.com/webhook",
  "events": ["job.started", "job.completed", "job.failed"]
}
```

## SDK

### Python
```
pip install finetuning-studio-sdk
```

### JavaScript
```
npm install finetuning-studio-sdk
```

## Support

- Documentation: https://docs.finetuning-studio.com
- Issues: https://github.com/finetuning-studio/api/issues
- Email: support@finetuning-studio.com
