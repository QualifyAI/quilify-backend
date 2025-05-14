from fastapi import APIRouter
from app.api.routes import auth, learning_path, skill_gap, resume, resume_analysis
 
api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(learning_path.router)
api_router.include_router(skill_gap.router)
api_router.include_router(resume.router) 
api_router.include_router(resume_analysis.router) 