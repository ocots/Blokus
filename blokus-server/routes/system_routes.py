from fastapi import APIRouter
import os
from datetime import datetime
from version import BACKEND_VERSION

router = APIRouter(tags=["System"])

PID = os.getpid()
START_TIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@router.get("/")
def read_root():
    return {
        "message": f"Welcome to Blokus API {BACKEND_VERSION}", 
        "version": BACKEND_VERSION,
        "pid": PID,
        "started_at": START_TIME
    }
