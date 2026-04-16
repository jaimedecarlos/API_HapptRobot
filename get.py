import requests

BASE = "https://unshaken-quote-rust.ngrok-free.dev"  # your ngrok URL
headers = {"x-api-key": "happyrobot-key-2024"}

# Get all loads
print(requests.get(f"{BASE}/calls", headers=headers).json())

# Get one load
print(requests.get(f"{BASE}/loads/CAO34288", headers=headers).json())