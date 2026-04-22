import os
import sys
from dotenv import load_dotenv
import pathlib

# Add the Backend directory to sys.path to import app
backend_dir = pathlib.Path(__file__).parent.parent
sys.path.append(str(backend_dir))

# Load .env
env_path = backend_dir / ".env"
load_dotenv(dotenv_path=env_path)

# Mock some things for app creation if necessary
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['SECRET_KEY'] = 'test-secret'

from app import create_app
from app.config import Config, DevelopmentConfig, ProductionConfig

def verify_cors():
    print("--- AeroGuard CORS Configuration Verification ---")
    
    # 1. Check .env directly
    print(f"\n1. Checking .env at {env_path}:")
    with open(env_path, 'r') as f:
        content = f.read()
        if 'https://aero-guard-deploy.vercel.app' in content:
            print("  [PASS] Vercel URL found in .env")
        else:
            print("  [FAIL] Vercel URL NOT found in .env")

    # 2. Check Development Config
    print("\n2. Checking DevelopmentConfig:")
    app_dev = create_app(DevelopmentConfig)
    origins_dev = app_dev.config.get("CORS_ORIGINS")
    print(f"  Origins: {origins_dev}")
    if 'https://aero-guard-deploy.vercel.app' in origins_dev:
        print("  [PASS] Vercel URL allowed in DevelopmentConfig")
    if '*' in origins_dev:
        print("  [PASS] '*' allowed in DevelopmentConfig")

    # 3. Check Production Config (Simulated)
    print("\n3. Checking ProductionConfig (Simulated):")
    # Production enforces env var, so we mock it
    os.environ['FLASK_ENV'] = 'production'
    os.environ['CORS_ORIGINS'] = 'https://aero-guard-deploy.vercel.app,http://localhost:3000'
    
    app_prod = create_app(ProductionConfig)
    origins_prod = app_prod.config.get("CORS_ORIGINS")
    print(f"  Origins: {origins_prod}")
    if 'https://aero-guard-deploy.vercel.app' in origins_prod:
        print("  [PASS] Vercel URL allowed in ProductionConfig")
    if 'http://localhost:3000' in origins_prod:
        print("  [PASS] Localhost allowed in ProductionConfig")
    
    print("\n--- Verification Complete ---")

if __name__ == "__main__":
    verify_cors()
