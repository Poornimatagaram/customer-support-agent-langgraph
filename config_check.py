"""
config_check.py

Validates that required environment variables are set BEFORE the
agent tries to run. Fails fast with a clear message, instead of
crashing confusingly deep inside some node later.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

REQUIRED_VARS = ["GOOGLE_API_KEY"]

# These are optional -- the agent works without them, just with
# reduced functionality (no LangSmith tracing). Worth warning about,
# not worth crashing over.
OPTIONAL_VARS = ["LANGCHAIN_API_KEY", "LANGCHAIN_TRACING_V2"]


def validate_config():
    missing_required = [var for var in REQUIRED_VARS if not os.getenv(var)]

    if missing_required:
        print("ERROR: Missing required environment variable(s):")
        for var in missing_required:
            print(f"  - {var}")
        print("\nAdd these to your .env file before running the agent.")
        sys.exit(1)   # Exit the program immediately with a non-zero status (signals failure)

    missing_optional = [var for var in OPTIONAL_VARS if not os.getenv(var)]
    if missing_optional:
        print("Note: optional environment variable(s) not set (tracing/observability will be disabled):")
        for var in missing_optional:
            print(f"  - {var}")

    print("Config check passed.\n")