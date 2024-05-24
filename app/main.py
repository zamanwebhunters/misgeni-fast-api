from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from zk import ZK
from datetime import datetime

app = FastAPI()

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
        zk = ZK(ip, port=port, timeout=10, password=0, force_udp=False, ommit_ping=False)
        conn = zk.connect()
        conn.disable_device()
        print("Connected successfully")

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
        print(f"Error: {str(e)}")
        return {"error": str(e)}

    finally:
        if conn:
            conn.enable_device()
            conn.disconnect()

@app.post("/get_attendance_data")
def read_attendance(request: AttendanceRequest):
    attendance_data = get_attendance_data(
        request.ip,
        request.port,
        request.start_time,
        request.end_time,
        request.status_codes
    )
    
    if "error" in attendance_data:
        raise HTTPException(status_code=500, detail=attendance_data["error"])

    return attendance_data
