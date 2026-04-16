"""
Simple CLI to add or remove API keys from api_keys.json.

Usage:
  python3 manage_keys.py add <key>
  python3 manage_keys.py remove <key>
  python3 manage_keys.py list
"""
import json
import sys
import os

KEYS_FILE = os.path.join(os.path.dirname(__file__), "api_keys.json")


def load():
    if not os.path.exists(KEYS_FILE):
        return []
    with open(KEYS_FILE) as f:
        return json.load(f)


def save(keys):
    with open(KEYS_FILE, "w") as f:
        json.dump(keys, f, indent=2)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    keys = load()

    if cmd == "list":
        if keys:
            print("\n".join(keys))
        else:
            print("No API keys configured.")

    elif cmd == "add":
        if len(sys.argv) < 3:
            print("Usage: python3 manage_keys.py add <key>")
            sys.exit(1)
        key = sys.argv[2]
        if key in keys:
            print(f"Key already exists: {key}")
        else:
            keys.append(key)
            save(keys)
            print(f"Added key: {key}")

    elif cmd == "remove":
        if len(sys.argv) < 3:
            print("Usage: python3 manage_keys.py remove <key>")
            sys.exit(1)
        key = sys.argv[2]
        if key not in keys:
            print(f"Key not found: {key}")
        else:
            keys.remove(key)
            save(keys)
            print(f"Removed key: {key}")

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
