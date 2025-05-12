from fastapi import APIRouter
from app.api.routes import auth, learning_path
 
api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(learning_path.router) 