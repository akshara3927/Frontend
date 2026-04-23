import os
from pymongo import MongoClient
from pathlib import Path

def load_secrets():
    """Load secrets from .streamlit/secrets.toml"""
    # Go up to project root (Frontend/) then find .streamlit
    base_path = Path(__file__).resolve()
    # database.py is at: src/modules/patientconsent/database.py
    # Need to go up 4 levels to reach root
    project_root = base_path.parent.parent.parent.parent
    secrets_path = project_root / ".streamlit" / "secrets.toml"
    
    if secrets_path.exists():
        import tomli
        with open(secrets_path, "rb") as f:
            return tomli.load(f)
    return {}

def get_mongo_uri():
    """Get MongoDB URI from environment or secrets file"""
    # Try environment variable first
    uri = os.environ.get("MONGO_URI")
    if uri:
        return uri
    
    # Try reading from secrets.toml file directly
    try:
        secrets = load_secrets()
        if "general" in secrets and "MONGO_URI" in secrets["general"]:
            return secrets["general"]["MONGO_URI"]
    except Exception:
        pass
    
    return "mongodb://localhost:27017"

# Lazy connection - only connects when actually used
_client = None

def get_client():
    global _client
    if _client is None:
        _client = MongoClient(get_mongo_uri())
    return _client

def get_db():
    return get_client()["mydatabase"]

# Legacy compatibility - keep these for existing code
collection = get_db()["users"]
consents = get_db()["consents"]
research = get_db()["research_studies"]
privacy_policies = get_db()["privacy_policies"]
permissions = get_db()["permissions"]
db = get_db()



