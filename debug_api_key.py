import os
import streamlit as st

# Mock st.secrets to avoid error if not present
if not hasattr(st, "secrets"):
    st.secrets = {}

def _load_api_key():
    print(f"CWD: {os.getcwd()}")
    
    # 1. Secrets
    try:
        if st.secrets.get("APIKEY"):
            print("Found in secrets")
            return st.secrets.get("APIKEY")
    except Exception:
        pass

    # 2. Environment Variable
    api_key = os.environ.get("APIKEY")
    if api_key:
        print("Found in os.environ")
        return api_key

    cwd = os.getcwd()
    
    # 3. api_key file
    api_key_path = os.path.join(cwd, "api_key")
    if os.path.isfile(api_key_path):
        print(f"Found api_key file at {api_key_path}")
        with open(api_key_path, "r") as f:
            return f.readline().strip()

    # 4. .env file
    env_path = os.path.join(cwd, ".env")
    if os.path.isfile(env_path):
        print(f"Found .env file at {env_path}")
        with open(env_path, "r") as f:
            content = f.read()
            print(f"Content length: {len(content)}")
            f.seek(0)
            for line in f:
                stripped = line.strip()
                if not stripped or stripped.startswith("#") or "=" not in stripped:
                    continue
                key, value = stripped.split("=", 1)
                # print(f"Checking key: '{key}'")
                if key.strip() == "APIKEY" and value.strip():
                    print("Found in .env")
                    return value.strip()
    else:
        print(f".env file NOT found at {env_path}")
        
    return None

key = _load_api_key()
if key:
    print(f"API Key loaded. Length: {len(key)}")
else:
    print("API Key NOT loaded.")
