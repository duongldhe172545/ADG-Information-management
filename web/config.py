import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'app.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
EXPORT_FOLDER = os.path.join(BASE_DIR, 'exports')

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# Ensure directories exist
for folder in [os.path.dirname(DB_PATH), UPLOAD_FOLDER, EXPORT_FOLDER]:
    os.makedirs(folder, exist_ok=True)
