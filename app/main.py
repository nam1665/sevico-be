from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import logging
from contextlib import asynccontextmanager
from app.config.settings import get_settings
from app.config.database import db
from app.routes import auth_routes
import secrets


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# HTTP Basic Auth for docs
security = HTTPBasic()


def verify_docs_credentials(credentials: HTTPBasicCredentials = Depends(security)) -> bool:
    """
    Verify credentials for accessing API documentation.
    Default username: admin, password: admin
    Change these in environment variables in production.
    """
    settings = get_settings()
    
    # You can configure these via environment variables
    docs_username = getattr(settings, 'docs_username', 'admin')
    docs_password = getattr(settings, 'docs_password', 'admin')
    
    # Verify credentials
    is_username_correct = secrets.compare_digest(credentials.username, docs_username)
    is_password_correct = secrets.compare_digest(credentials.password, docs_password)
    
    if not (is_username_correct and is_password_correct):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials for documentation access",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return True


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Starting FastAPI application...")
    try:
        db.connect()
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down FastAPI application...")
    db.disconnect()
    logger.info("Database connection closed")


# Create FastAPI app with custom docs settings
app = FastAPI(
    title="Sevico API",
    description="Complete authentication system with JWT and MongoDB",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(auth_routes.router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Sevico API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Sevico API"
    }


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug
    )
