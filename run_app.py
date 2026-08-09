import os
import sys
import socket
import uvicorn
from dotenv import load_dotenv

load_dotenv()

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "192.168.1.100"

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
LOCAL_IP = get_local_ip()

if __name__ == "__main__":
    print("=" * 75)
    print(" [AI INTERVIEW PREPARATION & PERFORMANCE EVALUATION SYSTEM]")
    print("=" * 75)
    print(f" Local PC Access:   http://127.0.0.1:{PORT}")
    print(f" Other Devices URL: http://{LOCAL_IP}:{PORT}")
    print(f" API Docs:          http://127.0.0.1:{PORT}/docs")
    print("=" * 75)
    
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=False)
