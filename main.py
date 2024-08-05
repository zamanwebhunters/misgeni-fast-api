from fastapi import FastAPI, HTTPException
from typing import Optional, Dict, Any
import logging
from attendance_db_manager import fetch_org_info_from_db


app = FastAPI()
logging.basicConfig(level=logging.INFO)
 
@app.get("/mark_attendance")
def server_running():
    res = fetch_org_info_from_db()
    return res


@app.get("/")
def server_running():
    logging.info("Server check")
    return {"message": "server is running"}

 
