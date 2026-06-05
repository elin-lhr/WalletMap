import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')

# Tests for WalletMap — to be written
