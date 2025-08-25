import os
from pathlib import Path

APP_DIR = Path(os.path.expanduser("~/.clinic_app"))
DB_PATH = APP_DIR / "clinic.db"
DOCS_DIR = APP_DIR / "documents"
TEMPLATES_DIR = APP_DIR / "templates"
ASSETS_DIR = Path(__file__).resolve().parent / "assets"

APP_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_CSS_PATH = ASSETS_DIR / "templates" / "style.css"
