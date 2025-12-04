# Sevico API - FastAPI Authentication System

A complete FastAPI project with JWT authentication, MongoDB integration, email verification, and password reset functionality.

## Features

✅ **User Authentication**
- Sign up with email and password
- Email verification with 6-digit code
- Sign in with JWT tokens
- Password reset with secure tokens
- Token validation endpoint

✅ **Security**
- Password hashing with bcrypt (passlib)
- JWT token generation and verification
- SMTP email configuration
- Protected routes with token validation

✅ **Database**
- MongoDB integration
- Clean data models and schemas
- User data persistence

✅ **Code Quality**
- Clean, scalable project structure
- Pydantic models for validation
- Comprehensive error handling
- Logging configured
- Production-ready

## Project Structure

```
app/
├── main.py                 # FastAPI application entry point
├── config/
│   ├── settings.py        # Environment configuration (Pydantic Settings)
│   └── database.py        # MongoDB connection management
├── models/
│   └── user_model.py      # User data model
├── schemas/
│   └── user_schema.py     # Pydantic request/response schemas
├── routes/
│   └── auth_routes.py     # Authentication API endpoints
├── services/
│   ├── auth_service.py    # Authentication business logic
│   └── email_service.py   # SMTP email functionality
└── utils/
    ├── jwt_helper.py      # JWT token creation and verification
    └── password_helper.py # Password hashing and verification
```

## Installation

### 1. Clone and Setup

**Using Poetry (Recommended)**

```bash
cd /home/ubuntu/sevico-be
poetry install
poetry shell  # Activate the virtual environment
```

**Using pip (Alternative)**

```bash
cd /home/ubuntu/sevico-be
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Edit `.env` file and set your configuration:

```env
# FastAPI Configuration
FASTAPI_ENV=production
DEBUG=False
SECRET_KEY=your-secret-key-here

# Server Configuration
APP_HOST=0.0.0.0
APP_PORT=8002

# MongoDB Configuration (with authentication)
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_USERNAME=your-username
MONGODB_PASSWORD=your-password
MONGODB_DB_NAME=sevico_db
MONGODB_AUTH_SOURCE=admin

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Email Configuration (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_TLS=True
SENDER_EMAIL=your-email@gmail.com
SENDER_NAME=Sevico
```

### 3. Install Dependencies

```bash
poetry install
```

Or if using pip:

```bash
pip install -r requirements.txt
```

### 4. Run the Application

**Using Poetry:**

```bash
poetry run python -m app.main
# or with uvicorn directly
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

**Using pip:**

```bash
python -m app.main
# or
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

The API will be available at `http://localhost:8002`

**API Documentation:**
- Swagger UI: `http://localhost:8002/docs`
- ReDoc: `http://localhost:8002/redoc`

## API Endpoints

### Authentication Endpoints

#### 1. Sign Up
**POST** `/api/auth/signup`

Request:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

Response:
```json
{
  "email": "user@example.com",
  "message": "User registered successfully. Please verify your email."
}
```

---

#### 2. Verify Email
**POST** `/api/auth/verify-email`

Request:
```json
{
  "email": "user@example.com",
  "verification_code": "123456"
}
```

Response:
```json
{
  "message": "Email verified successfully"
}
```

---

#### 3. Sign In
**POST** `/api/auth/signin`

Request:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "email": "user@example.com"
}
```

---

#### 4. Validate Token
**POST** `/api/auth/validate-token`

Request:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Response (Valid):
```json
{
  "is_valid": true,
  "email": "user@example.com",
  "message": "Token is valid"
}
```

Response (Invalid):
```json
{
  "is_valid": false,
  "email": null,
  "message": "Invalid or expired token"
}
```

---

#### 5. Request Password Reset
**POST** `/api/auth/password-reset`

Request:
```json
{
  "email": "user@example.com"
}
```

Response:
```json
{
  "message": "Password reset email sent successfully"
}
```

---

#### 6. Confirm Password Reset
**POST** `/api/auth/password-reset-confirm`

Request:
```json
{
  "email": "user@example.com",
  "reset_token": "abc123def456...",
  "new_password": "NewPassword123"
}
```

Response:
```json
{
  "message": "Password reset successfully"
}
```

---

#### 7. Get Current User Info
**GET** `/api/auth/me`

Headers:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Response:
```json
{
  "email": "user@example.com",
  "is_verified": true,
  "created_at": "2024-01-15T10:30:00"
}
```

---

### Health Check

#### Health Check Endpoint
**GET** `/health`

Response:
```json
{
  "status": "healthy",
  "service": "Sevico API"
}
```

---

## MongoDB Schema

### Users Collection

```javascript
{
  _id: ObjectId,
  email: String,
  password_hash: String,
  is_verified: Boolean,
  verification_code: String (nullable),
  verification_code_expires_at: DateTime (nullable),
  password_reset_token: String (nullable),
  password_reset_token_expires_at: DateTime (nullable),
  created_at: DateTime,
  updated_at: DateTime
}
```

## Security Considerations

1. **Password Hashing**: Uses bcrypt via passlib
2. **JWT Tokens**: HS256 algorithm (change SECRET_KEY in production)
3. **Email Verification**: 6-digit codes expire after 15 minutes
4. **Password Reset**: Tokens expire after 1 hour
5. **CORS**: Currently allows all origins (configure for production)

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `FASTAPI_ENV` | development | Environment mode |
| `DEBUG` | True | Debug mode |
| `APP_PORT` | 8002 | Application port |
| `MONGODB_HOST` | localhost | MongoDB server host |
| `MONGODB_PORT` | 27017 | MongoDB server port |
| `MONGODB_USERNAME` | - | MongoDB username |
| `MONGODB_PASSWORD` | - | MongoDB password |
| `MONGODB_DB_NAME` | sevico_db | Database name |
| `MONGODB_AUTH_SOURCE` | admin | Authentication database |
| `JWT_SECRET_KEY` | - | JWT signing secret (change in production) |
| `JWT_ALGORITHM` | HS256 | JWT algorithm |
| `JWT_EXPIRATION_HOURS` | 24 | Token expiration time |
| `SMTP_HOST` | smtp.gmail.com | SMTP server host |
| `SMTP_PORT` | 587 | SMTP server port |
| `SMTP_USERNAME` | - | SMTP username |
| `SMTP_PASSWORD` | - | SMTP password |
| `SMTP_TLS` | True | Enable TLS |

## Testing with cURL

### Sign Up
```bash
curl -X POST "http://localhost:8002/api/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123"
  }'
```

### Verify Email
```bash
curl -X POST "http://localhost:8002/api/auth/verify-email" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "verification_code": "123456"
  }'
```

### Sign In
```bash
curl -X POST "http://localhost:8002/api/auth/signin" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123"
  }'
```

### Get Current User
```bash
curl -X GET "http://localhost:8002/api/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Error Handling

The API returns appropriate HTTP status codes:

- `200 OK` - Successful request
- `201 Created` - Resource created
- `400 Bad Request` - Invalid input or validation error
- `401 Unauthorized` - Authentication failed or missing token
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Production Deployment

Before deploying to production:

1. **Change all secrets in `.env`**:
   - `SECRET_KEY`
   - `JWT_SECRET_KEY`

2. **Configure SMTP credentials** with your email provider

3. **Set `DEBUG=False`** in `.env`

4. **Use a production-grade ASGI server**:
   ```bash
   # With Poetry
   poetry run gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
   
   # Or with pip
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
   ```

5. **Configure CORS** to allow only your domain:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://yourdomain.com"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

6. **Use HTTPS** with a valid SSL certificate

7. **Set up MongoDB Atlas** or a managed MongoDB service

## Dependencies

All dependencies are managed by Poetry in `pyproject.toml`:

**Production Dependencies:**
- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **pydantic** - Data validation
- **pymongo** - MongoDB driver
- **passlib** - Password hashing
- **python-jose** - JWT handling
- **email-validator** - Email validation

**Development Dependencies:**
- **pytest** - Testing framework
- **pytest-asyncio** - Async test support
- **httpx** - HTTP client for testing
- **black** - Code formatter
- **flake8** - Code linter
- **mypy** - Type checker
- **isort** - Import sorter

For `requirements.txt` (legacy alternative), use `poetry export`.

## License

This project is provided as-is for educational and production use.

## Support

For issues or questions, please refer to the FastAPI documentation:
- https://fastapi.tiangolo.com/
- https://pymongo.readthedocs.io/
- https://passlib.readthedocs.io/

---

**Ready to use!** Configure your `.env` file and run the application.
