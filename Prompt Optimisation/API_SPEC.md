# Prompt Optimization Platform - API Specification

## Base URL
```
http://localhost:8000/api
```

## Authentication
All endpoints (except `/auth/register` and `/auth/token`) require a Bearer token:
```
Authorization: Bearer <YOUR_ACCESS_TOKEN>
```

---

## Authentication Endpoints

### Register User
**POST** `/auth/register`

Creates a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2024-08-08T10:00:00"
}
```

**Error Responses:**
- `400 Bad Request`: Email already registered
- `422 Unprocessable Entity`: Invalid input format

---

### Login User
**POST** `/auth/token`

Authenticates user and returns access token.

**Request Body (Form Data):**
```
username=user@example.com&password=securepassword123
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid credentials

---

### Get Current User
**GET** `/auth/me`

Returns the authenticated user's information.

**Headers Required:**
```
Authorization: Bearer <ACCESS_TOKEN>
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2024-08-08T10:00:00"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired token

---

## Prompt Endpoints

### Create Prompt
**POST** `/prompts/`

Creates a new prompt with initial version.

**Headers Required:**
```
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "Customer Support Assistant",
  "description": "A prompt for handling customer inquiries",
  "content": "You are a helpful customer support assistant. Answer the following question: {query}",
  "model": "gpt-3.5-turbo",
  "tags": ["support", "chatbot", "customer-service"]
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "title": "Customer Support Assistant",
  "description": "A prompt for handling customer inquiries",
  "content": "You are a helpful customer support assistant...",
  "model": "gpt-3.5-turbo",
  "tags": ["support", "chatbot", "customer-service"],
  "author_id": 1,
  "is_active": true,
  "created_at": "2024-08-08T10:00:00",
  "updated_at": "2024-08-08T10:00:00",
  "versions": [
    {
      "id": 1,
      "prompt_id": 1,
      "version_number": 1,
      "content": "You are a helpful customer support assistant...",
      "model": "gpt-3.5-turbo",
      "change_description": "Initial version",
      "created_at": "2024-08-08T10:00:00"
    }
  ],
  "metadata": {
    "id": 1,
    "prompt_id": 1,
    "performance_score": 0,
    "token_count": 0,
    "usage_count": 0,
    "last_used": null,
    "custom_data": {}
  }
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid token
- `422 Unprocessable Entity`: Invalid input

---

### List Prompts
**GET** `/prompts/`

Returns paginated list of prompts for authenticated user.

**Headers Required:**
```
Authorization: Bearer <ACCESS_TOKEN>
```

**Query Parameters:**
- `skip` (int, default: 0): Number of prompts to skip
- `limit` (int, default: 10): Number of prompts to return

**Response:** `200 OK`
```json
{
  "total": 5,
  "prompts": [
    {
      "id": 1,
      "title": "Customer Support Assistant",
      "description": "A prompt for handling customer inquiries",
      "content": "You are a helpful customer support assistant...",
      "model": "gpt-3.5-turbo",
      "tags": ["support", "chatbot"],
      "author_id": 1,
      "is_active": true,
      "created_at": "2024-08-08T10:00:00",
      "updated_at": "2024-08-08T10:00:00",
      "versions": [...],
      "metadata": {...}
    }
  ]
}
```

---

### Get Prompt
**GET** `/prompts/{prompt_id}`

Returns details of a specific prompt.

**Path Parameters:**
- `prompt_id` (int): ID of the prompt

**Headers Required:**
```
Authorization: Bearer <ACCESS_TOKEN>
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "Customer Support Assistant",
  "description": "A prompt for handling customer inquiries",
  "content": "You are a helpful customer support assistant...",
  "model": "gpt-3.5-turbo",
  "tags": ["support", "chatbot"],
  "author_id": 1,
  "is_active": true,
  "created_at": "2024-08-08T10:00:00",
  "updated_at": "2024-08-08T10:00:00",
  "versions": [...],
  "metadata": {...}
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid token
- `403 Forbidden`: Not authorized to access this prompt
- `404 Not Found`: Prompt not found

---

### Update Prompt
**PUT** `/prompts/{prompt_id}`

Updates a prompt (partial or full update).

**Path Parameters:**
- `prompt_id` (int): ID of the prompt

**Headers Required:**
```
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json
```

**Request Body (all fields optional):**
```json
{
  "title": "Updated Title",
  "description": "Updated description",
  "content": "Updated content",
  "model": "gpt-4",
  "tags": ["tag1", "tag2"]
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "Updated Title",
  "description": "Updated description",
  ...
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid token
- `403 Forbidden`: Not authorized
- `404 Not Found`: Prompt not found

---

### Delete Prompt
**DELETE** `/prompts/{prompt_id}`

Deletes a prompt and all its versions.

**Path Parameters:**
- `prompt_id` (int): ID of the prompt

**Headers Required:**
```
Authorization: Bearer <ACCESS_TOKEN>
```

**Response:** `204 No Content`

**Error Responses:**
- `401 Unauthorized`: Invalid token
- `403 Forbidden`: Not authorized
- `404 Not Found`: Prompt not found

---

## Prompt Versioning Endpoints

### Create Version
**POST** `/prompts/{prompt_id}/versions`

Creates a new version of an existing prompt.

**Path Parameters:**
- `prompt_id` (int): ID of the prompt

**Headers Required:**
```
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json
```

**Request Body:**
```json
{
  "content": "Updated prompt content with improvements",
  "model": "gpt-4",
  "change_description": "Improved clarity and added examples"
}
```

**Response:** `201 Created`
```json
{
  "version_id": 2,
  "version_number": 2
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid token
- `403 Forbidden`: Not authorized
- `404 Not Found`: Prompt not found

---

### List Versions
**GET** `/prompts/{prompt_id}/versions`

Returns all versions of a prompt in chronological order.

**Path Parameters:**
- `prompt_id` (int): ID of the prompt

**Headers Required:**
```
Authorization: Bearer <ACCESS_TOKEN>
```

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "prompt_id": 1,
    "version_number": 1,
    "content": "Initial prompt content",
    "model": "gpt-3.5-turbo",
    "change_description": "Initial version",
    "created_at": "2024-08-08T10:00:00"
  },
  {
    "id": 2,
    "prompt_id": 1,
    "version_number": 2,
    "content": "Updated prompt content",
    "model": "gpt-4",
    "change_description": "Improved clarity",
    "created_at": "2024-08-08T10:30:00"
  }
]
```

**Error Responses:**
- `401 Unauthorized`: Invalid token
- `403 Forbidden`: Not authorized
- `404 Not Found`: Prompt not found

---

### Rollback to Version
**POST** `/prompts/{prompt_id}/rollback/{version_id}`

Rolls back to a previous version by creating a new version with the old content.

**Path Parameters:**
- `prompt_id` (int): ID of the prompt
- `version_id` (int): ID of the version to rollback to

**Headers Required:**
```
Authorization: Bearer <ACCESS_TOKEN>
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "Customer Support Assistant",
  "content": "Content from version 1",
  "model": "gpt-3.5-turbo",
  ...
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid token
- `403 Forbidden`: Not authorized
- `404 Not Found`: Prompt or version not found

---

### Compare Versions
**POST** `/prompts/{prompt_id}/compare`

Compares two versions and returns the differences using unified diff format.

**Path Parameters:**
- `prompt_id` (int): ID of the prompt

**Headers Required:**
```
Authorization: Bearer <ACCESS_TOKEN>
```

**Query Parameters:**
- `version_1_id` (int): ID of first version
- `version_2_id` (int): ID of second version

**Response:** `200 OK`
```json
{
  "version_1_id": 1,
  "version_2_id": 2,
  "version_1_content": "Original content",
  "version_2_content": "Updated content",
  "differences": [
    "--- ",
    "+++ ",
    "@@ -1 +1 @@",
    "-Original content",
    "+Updated content"
  ]
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid token
- `403 Forbidden`: Not authorized
- `404 Not Found`: Prompt or version not found

---

## Response Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 204 | No Content - Successful deletion |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Missing or invalid token |
| 403 | Forbidden - Not authorized to access resource |
| 404 | Not Found - Resource not found |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error - Server error |

---

## Data Models

### User
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2024-08-08T10:00:00"
}
```

### Prompt
```json
{
  "id": 1,
  "title": "Prompt Title",
  "description": "Optional description",
  "content": "Actual prompt content",
  "model": "gpt-3.5-turbo",
  "tags": ["tag1", "tag2"],
  "author_id": 1,
  "is_active": true,
  "created_at": "2024-08-08T10:00:00",
  "updated_at": "2024-08-08T10:00:00",
  "versions": [],
  "metadata": {}
}
```

### PromptVersion
```json
{
  "id": 1,
  "prompt_id": 1,
  "version_number": 1,
  "content": "Prompt content",
  "model": "gpt-3.5-turbo",
  "change_description": "Description of changes",
  "created_at": "2024-08-08T10:00:00"
}
```

### PromptMetadata
```json
{
  "id": 1,
  "prompt_id": 1,
  "performance_score": 0,
  "token_count": 0,
  "usage_count": 0,
  "last_used": null,
  "custom_data": {}
}
```

---

## Rate Limiting

Not currently implemented, but recommended for production.

---

## Pagination

List endpoints support pagination:
- `skip`: Offset for pagination (default: 0)
- `limit`: Number of items per page (default: 10, max: 100)

Example:
```
GET /api/prompts/?skip=0&limit=20
```

---

## Error Handling

All errors follow this format:
```json
{
  "detail": "Error description"
}
```

---

## Example Workflows

### Create and Version a Prompt

1. Register/Login to get token
2. Create prompt: `POST /prompts/`
3. Create version: `POST /prompts/{id}/versions`
4. Compare versions: `POST /prompts/{id}/compare?v1=1&v2=2`
5. Rollback if needed: `POST /prompts/{id}/rollback/{version_id}`

### Full Prompt Lifecycle

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass123","full_name":"John"}'

# Login
curl -X POST http://localhost:8000/api/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=pass123"

# Create prompt
curl -X POST http://localhost:8000/api/prompts/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"My Prompt","content":"..."}'

# List prompts
curl http://localhost:8000/api/prompts/ \
  -H "Authorization: Bearer TOKEN"
```

---

## Performance Considerations

- Indexes on frequently queried fields (email, author_id, prompt_id)
- Eager loading of related objects to reduce queries
- Pagination for list endpoints
- Connection pooling for database

---

## Security

- All endpoints require authentication (except register/login)
- Passwords hashed with bcrypt
- JWT tokens with expiration
- Authorization checks on user-owned resources
- SQL injection prevention through ORM

---

## Versioning

API Version: `1.0.0`

Current status: **Stable**

---

For more information, see:
- [README.md](README.md) - Overview and features
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Setup and installation
- Interactive API docs at `http://localhost:8000/docs`
