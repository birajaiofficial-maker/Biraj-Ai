from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="BIRAJ AI",
    description="API-first AI Customer Support & Business Automation platform",
    version="0.1.0",
)

# Local-development origins only. Configure production origins before deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://127.0.0.1"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.get("/", tags=["System"])
def home():
    return {
        "project": "BIRAJ AI",
        "message": "Welcome to BIRAJ AI API",
        "status": "running",
        "version": app.version,
        "docs": "/docs",
    }


@app.get("/health", tags=["System"])
def health():
    return {"status": "healthy", "service": "BIRAJ AI"}


@app.get("/api/v1/services", tags=["Services"])
def list_services():
    return {
        "version": "v1",
        "status": "foundation",
        "services": [
            {"id": "customer-support", "name": "AI Customer Support", "status": "planned"},
            {"id": "knowledge-base", "name": "AI Knowledge Base", "status": "planned"},
            {"id": "multilingual", "name": "AI Language Assistant", "status": "planned"},
        ],
    }
