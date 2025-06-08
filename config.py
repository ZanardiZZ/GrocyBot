from dotenv import load_dotenv
import os
from openai import OpenAI

# Load environment variables once for the whole application
load_dotenv()

# Environment constants
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROCY_URL = os.getenv("GROCY_URL", "").rstrip("/")
GROCY_API_KEY = os.getenv("GROCY_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTICAPTCHA_KEY = os.getenv("ANTICAPTCHA_KEY")
DEFAULT_LOCATION_ID = int(os.getenv("DEFAULT_LOCATION_ID", "1"))

# Shared OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)
