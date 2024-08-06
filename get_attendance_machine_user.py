# zk_utils.py
import logging
from zk import ZK, const

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_users(ip: str, port: int):
    conn = None
    try:
        zk = ZK(ip, port=port, timeout=5, password=0, force_udp=False, ommit_ping=False)
        conn = zk.connect()
        conn.disable_device()
        users = conn.get_users()
        user_list = []
        for user in users:
            user_list.append({
                'uid': user.uid,
                'name': user.name,
                'user_id': user.user_id,
                'card': user.card,
                'group_id': user.group_id,
             
            })
        conn.enable_device()
        return user_list
    except Exception as e:
        logger.error(f"Process terminated: {e}")
        return []
    finally:
        if conn:
            conn.disconnect()
