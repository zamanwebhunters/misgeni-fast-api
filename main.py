from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
from attendance_db_manager import fetch_org_info_from_db


app = FastAPI()
logging.basicConfig(level=logging.INFO)

class AttendanceRequest(BaseModel):
    ip: str
    port: int
    start_time: str
    end_time: str
    status_codes: Optional[Dict[int, str]] = None


# @app.post("/get_attendance_data")
# def read_attendance(request: AttendanceRequest):
#     logging.info(f"Received request: {request}")

#     attendance_data = get_attendance_data(
#         request.ip,
#         request.port,
#         request.start_time,
#         request.end_time,
#         request.status_codes
#     )
    
#     if "error" in attendance_data:
#         logging.error(f"Error in attendance data: {attendance_data['error']}")
#         raise HTTPException(status_code=500, detail=attendance_data["error"])
#     logging.info("Data fetched successfully")

#     if attendance_data:
#        insert_attandance_to_db(attendance_data, '103')
#     return {"response": res}

@app.get("/mark_attendance")
def server_running():
    res = fetch_org_info_from_db()
    return res


@app.get("/")
def server_running():
    logging.info("Server check")
    return {"message": "server is running"}

 
