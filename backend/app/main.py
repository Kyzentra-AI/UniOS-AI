from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import auth, profile, memory, planning, history, chat

app = FastAPI(
    title="UniOS.ai Backend API",
    description="FastAPI Backend for User Authentication, Student Profile & AI Memory System (Epic 1 & Epic 2)",
    version="1.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(memory.router)
app.include_router(planning.router)
app.include_router(history.router)
app.include_router(chat.router)

@app.get("/")
async def root():
    return {"message": "Welcome to UniOS.ai Backend API. Go to /api/docs for API documentation."}

