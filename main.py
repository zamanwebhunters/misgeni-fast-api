from fastapi import FastAPI, HTTPException
from typing import Optional, Dict, Any
from fastapi.middleware.cors import CORSMiddleware
import logging
from pydantic import BaseModel
from attendance_db_manager import fetch_org_info_from_db
from get_attendance_machine_user import get_users

app = FastAPI()
logging.basicConfig(level=logging.INFO)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class MachineInfo(BaseModel):
    ip: str
    port: int

 
@app.get("/mark_attendance")
def server_running():
    res = fetch_org_info_from_db()
    return res

@app.post("/get_machine_users")
def fetch_users(machine_info: MachineInfo):
    try:
        users = get_users(machine_info.ip, machine_info.port)
        if not users:
            raise HTTPException(status_code=404, detail="No users found or unable to connect to the device")
        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def server_running():
    logging.info("Server check")
    return {"message": "server is running"}

 
