import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Directory setup
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# Dataset path
DATASET_PATH = DATA_DIR / "tools_dataset.json"

# Gemini Configuration (Updated for v0.8.5)
GEMINI_API_KEY = os.getenv("AIzaSyDrQHMAwzP-uwq5L2hsLiZ8nIQUWEWEdZ0")
GEMINI_MODEL = "gemini-1.5-flash"  # Current best free-tier model
# Alternatives if needed:
# "gemini-1.5-pro" (more capable but higher cost)
# "gemini-1.0-pro" (legacy, may not work for new accounts)