from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from zk import ZK
from datetime import datetime
import logging

app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.INFO)

class AttendanceRequest(BaseModel):
    ip: str
    port: int
    start_time: str
    end_time: str
    status_codes: Optional[Dict[int, str]] = None

def interpret_event(punch: int, status_codes: Optional[Dict[int, str]]) -> str:
    return status_codes.get(punch, "Unknown event") if status_codes else "Unknown event"

def get_attendance_data(ip: str, port: int, start_time_str: str, end_time_str: str, status_codes: Optional[Dict[int, str]] = None) -> Any:
    conn = None
    try:
        logging.info(f"Connecting to ZK device at {ip}:{port}")
        
        zk = ZK(ip, port=port, timeout=30, password=0, force_udp=False, ommit_ping=False, encoding='UTF-8')
        conn = zk.connect()
        conn.disable_device()

        logging.info("Connected successfully")

        start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')

        users = conn.get_users()
        user_dict = {user.user_id: user.name for user in users}
        attendance = conn.get_attendance()
        
        attendance_data = []

        for record in attendance:
            if start_time <= record.timestamp <= end_time:
                user_id = record.user_id
                user_name = user_dict.get(user_id, "Unknown")
                timestamp = record.timestamp
                event_type = interpret_event(record.punch, status_codes)
                attendance_data.append({
                    "user_id": user_id,
                    "user_name": user_name,
                    "timestamp": timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    "event_type": event_type
                })

        return attendance_data

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return {"error": str(e)}

    finally:
        if conn:
            conn.enable_device()
            conn.disconnect()
            logging.info("Disconnected from device")

@app.post("/get_attendance_data")
def read_attendance(request: AttendanceRequest):
    logging.info(f"Received request: {request}")
    attendance_data = get_attendance_data(
        request.ip,
        request.port,
        request.start_time,
        request.end_time,
        request.status_codes
    )
    
    if "error" in attendance_data:
        logging.error(f"Error in attendance data: {attendance_data['error']}")
        raise HTTPException(status_code=500, detail=attendance_data["error"])

    logging.info("Data fetched successfully")
    return attendance_data

@app.get("/")
def server_running():
    logging.info("Server check")
    return {"message": "server is running"}
