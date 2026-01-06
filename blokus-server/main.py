import sys
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add engine to path (legacy support)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../blokus-engine/src")))

from version import BACKEND_VERSION
from routes import game_routes, ai_routes, system_routes

def create_app() -> FastAPI:
    """Application Factory"""
    app = FastAPI(
        title="Blokus API", 
        description="API for Blokus Game Engine", 
        version=BACKEND_VERSION
    )

    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include Routes
    app.include_router(system_routes.router)
    app.include_router(game_routes.router)
    app.include_router(ai_routes.router)
    
    return app

app = create_app()

if __name__ == "__main__":
    print(f"🚀 Blokus Backend {BACKEND_VERSION} Starting...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
