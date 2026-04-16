"""
Generates 20 random load entries and POSTs them to the API.
Run with the server already started:  python3 seed_data.py
"""
import random
import string
import json
import urllib.request
import urllib.error

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BASE_URL = "http://localhost:8000"
API_KEY  = "happyrobot-key-2024"

# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------
CITIES = [
    "Chicago, IL",
    "Dallas, TX",
    "Los Angeles, CA",
    "Atlanta, GA",
    "New York, NY",
    "Miami, FL",
]

EQUIPMENT_TYPES = ["Dry Van", "Flatbed", "Reefer"]

COMMODITIES = [
    "General Freight", "Produce", "Electronics",
    "Auto Parts", "Building Materials", "Frozen Foods",
    "Steel Coils", "Paper Products",
]

NOTES_POOL = [
    "Team driver required",
    "No touch freight",
    "Lumper available at destination",
    "Hazmat certified driver needed",
    "Drop and hook",
    "Live load/unload",
    "",
    "",  # weight toward blank notes
    "",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def random_load_id(existing: set) -> str:
    while True:
        letters = "".join(random.choices(string.ascii_uppercase, k=3))
        numbers = "".join(random.choices(string.digits, k=5))
        load_id = letters + numbers
        if load_id not in existing:
            existing.add(load_id)
            return load_id


def random_datetime(base_day: int) -> str:
    hour = random.choice([6, 7, 8, 10, 12, 14, 16])
    return f"2026-05-{base_day:02d} {hour:02d}:00"


def build_load(existing_ids: set) -> dict:
    origin, destination = random.sample(CITIES, 2)
    pickup_day  = random.randint(1, 20)
    delivery_day = pickup_day + random.randint(1, 3)

    return {
        "load_id":           random_load_id(existing_ids),
        "origin":            origin,
        "destination":       destination,
        "equipment_type":    random.choice(EQUIPMENT_TYPES),
        "pickup_datetime":   random_datetime(pickup_day),
        "delivery_datetime": random_datetime(min(delivery_day, 28)),
        "loadboard_rate":    round(random.uniform(1200, 4500), 2),
        "weight":            round(random.uniform(10000, 44000), 1),
        "commodity_type":    random.choice(COMMODITIES),
        "num_of_pieces":     random.randint(1, 26),
        "miles":             round(random.uniform(300, 2200), 1),
        "dimensions":        random.choice(["48x96x60", "53x96x110", "40x96x72", "48x102x96"]),
        "notes":             random.choice(NOTES_POOL),
    }


def post_load(load: dict) -> tuple[int, str]:
    data = json.dumps(load).encode()
    req  = urllib.request.Request(
        f"{BASE_URL}/loads",
        data=data,
        headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    existing_ids: set = set()
    loads = [build_load(existing_ids) for _ in range(20)]

    print(f"Posting {len(loads)} loads to {BASE_URL} ...\n")
    success = 0
    for load in loads:
        status, body = post_load(load)
        icon = "OK" if status == 201 else "FAIL"
        print(f"  [{icon}] {load['load_id']}  {load['origin']:20s} -> {load['destination']:20s}  {load['equipment_type']:10s}  ${load['loadboard_rate']:,.2f}  (HTTP {status})")
        if status == 201:
            success += 1
        else:
            print(f"         Error: {body}")

    print(f"\nDone. {success}/{len(loads)} loads created successfully.")


if __name__ == "__main__":
    main()