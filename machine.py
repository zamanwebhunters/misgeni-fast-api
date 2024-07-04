from typing import Optional, Dict, Any
from zk import ZK
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

def interpret_event(punch: int, status_codes: Optional[Dict[str, str]]) -> str:
    for event, code in status_codes.items():
        if str(punch) == code:
            return event
    return "Unknown event"

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
                timestamp_str = record.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                event_type = interpret_event(record.punch, status_codes)
                attendance_data.append({
                    "user_id": user_id,
                    "user_name": user_name,
                    "timestamp": timestamp_str,
                    "event_type": event_type
                })     
        return attendance_data

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise 

    finally:
        if conn:
            conn.enable_device()
            conn.disconnect()
            logging.info("Disconnected from device")
