import os
from pathlib import Path

# Same loader from settings.py
BASE_DIR = Path(__file__).resolve().parent

def _load_dotenv():
    env_path = BASE_DIR / '.env'
    if not env_path.exists():
        print(f"❌ .env file NOT found at: {env_path}")
        return
    print(f"✅ .env file found at: {env_path}")
    
    with env_path.open() as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            key, value = line.split('=', 1)
            key = key.strip()
            if not key or key in os.environ:
                continue
            os.environ[key] = value.strip().strip('"').strip("'")
            print(f"  Loaded: {key} = {'*' * len(value.strip()) if 'PASSWORD' in key else value.strip()[:20]}")

_load_dotenv()

# Check database settings
print("\n📊 Database Configuration:")
print(f"  DB_NAME: {os.getenv('DB_NAME', 'NOT SET')}")
print(f"  DB_USER: {os.getenv('DB_USER', 'NOT SET')}")
print(f"  DB_PASSWORD: {'SET (' + str(len(os.getenv('DB_PASSWORD', ''))) + ' chars)' if os.getenv('DB_PASSWORD') else 'NOT SET'}")
print(f"  DB_HOST: {os.getenv('DB_HOST', 'NOT SET')}")
print(f"  DB_PORT: {os.getenv('DB_PORT', 'NOT SET')}")
