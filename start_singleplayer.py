import subprocess
import time
from client import Client

server = subprocess.Popen(["python3", "start_server.py", "9000"])

time.sleep(2)

client = Client('127.0.0.1', 9000)

try:
    client.start()
except KeyboardInterrupt:
    import sys, os
    try:
        sys.exit(0)
    except SystemExit:
        server.kill()
        os._exit(0)
finally:
    server.kill()
