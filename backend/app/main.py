from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import auth, onboarding, syllabus, roadmaps, missions, learning, assessments, build

app = FastAPI(
    title="UniOS.ai Backend API",
    description="FastAPI Backend for User Authentication",
    version="1.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)
#remove in production
#from app.core.request_logger_middleware import RequestLoggerMiddleware

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom standalone logger middleware remove in production
#app.add_middleware(RequestLoggerMiddleware)

# Include Routers
app.include_router(auth.router)
app.include_router(onboarding.router)
app.include_router(syllabus.router)
app.include_router(roadmaps.router)
app.include_router(missions.router)
app.include_router(learning.router)
app.include_router(assessments.router)
app.include_router(build.router)

@app.get("/")
async def root():
    return {"message": "Welcome to UniOS.ai Backend API. Go to /api/docs for API documentation."}

