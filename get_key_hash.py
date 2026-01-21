import os
import hashlib

def get_api_key():
    api_key = os.environ.get("APIKEY")
    if api_key:
        return api_key

    cwd = os.getcwd()
    env_path = os.path.join(cwd, ".env")
    if os.path.isfile(env_path):
        with open(env_path, "r") as f:
            for line in f:
                stripped = line.strip()
                if not stripped or stripped.startswith("#") or "=" not in stripped:
                    continue
                key, value = stripped.split("=", 1)
                if key.strip() == "APIKEY" and value.strip():
                    return value.strip()
    return None

api_key = get_api_key()
if api_key:
    # Calculate SHA256 hash
    key_hash = hashlib.sha256(api_key.strip().encode()).hexdigest()
    print(f"API Key Hash: {key_hash}")
else:
    print("APIKEY not found.")
