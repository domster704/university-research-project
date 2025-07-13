import socket
import uuid

try:
    AGENT_ID = socket.gethostname()
except Exception as e:
    AGENT_ID = str(uuid.uuid4())

SERVER_URL = "https://balancer.example.com:8000"
COLLECT_PERIOD = 0.25
