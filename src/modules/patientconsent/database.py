import os
from pymongo import MongoClient
from pathlib import Path

def load_secrets():
    base_path = Path(__file__).resolve()
    project_root = base_path.parent.parent.parent.parent
    secrets_path = project_root / ".streamlit" / "secrets.toml"
    
    if secrets_path.exists():
        import tomli
        with open(secrets_path, "rb") as f:
            return tomli.load(f)
    return {}

def get_mongo_uri():
    uri = os.environ.get("MONGO_URI")
    if uri:
        return uri
    
    try:
        secrets = load_secrets()
        if "general" in secrets and "MONGO_URI" in secrets["general"]:
            return secrets["general"]["MONGO_URI"]
    except Exception:
        pass
    
    return "mongodb://localhost:27017"

_client = None

def get_client():
    global _client
    if _client is None:
        _client = MongoClient(get_mongo_uri(), serverSelectionTimeoutMS=5000)
    return _client

def get_db():
    return get_client()["patientconsent"]

# Collections
db = get_db()
users = db["users"]
consents = db["consents"]
research = db["research_studies"]
privacy_policies = db["privacy_policies"]
permissions = db["permissions"]