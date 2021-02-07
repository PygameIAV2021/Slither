from sys import argv
from scripts.client import Client

print("\n\nFirst argument is the ip-address and second the port of the server.")
print("For example: 'python3 start_multiplayer.py 192.168.178.13 9001'.")
print("Source: https://github.com/PygameIAV2021/Slither")


ip = '127.0.0.1'
port = 9000
print(f"Default configuration is {ip}:{port}.\n\n")


if len(argv) > 1:
    ip = argv[1]
    if len(argv) > 2:
        port = argv[2]


client = Client(ip, port)

try:
    client.start()
except KeyboardInterrupt:
    import sys, os
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)