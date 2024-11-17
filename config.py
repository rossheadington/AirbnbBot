import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Retrieve values from the .env file
AIRBNB_USERNAME = os.getenv('AIRBNB_USERNAME')
AIRBNB_PASSWORD = os.getenv('AIRBNB_PASSWORD')
OPEN_AI_API_KEY = os.getenv('OPEN_AI_API_KEY')
