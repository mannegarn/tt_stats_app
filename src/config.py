# src/config.py
from pathlib import Path
import re

# Setup directory structure
# This has caused some issues with importing in other modules - not sure why

# points to roots of project
BASE_DIR = Path(__file__).parent.parent

# Data directories
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
INTERMEDIATE_DIR = DATA_DIR / "intermediate"
MASTER_DIR = DATA_DIR / "master"

# Sub-directories for organized raw storage
RAW_EVENTS_DIR = RAW_DIR / "events"
RAW_MATCHES_DIR = RAW_DIR / "match_details"
RAW_PLAYERS_DIR = RAW_DIR / "player_details"
RAW_EVENT_MATCHES_DIR = RAW_DIR / "event_matches"

# Ensure ALL directories exist when config is imported
for directory in [
    RAW_EVENTS_DIR,
    RAW_MATCHES_DIR,
    RAW_PLAYERS_DIR,
    INTERMEDIATE_DIR,
    MASTER_DIR,
    RAW_EVENT_MATCHES_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)


## Event filtering
EXCLUDED_EVENT_TERMS = {
    "cadet",
    "junior",
    "youth",
    "under",
    "girls",
    "boys",  # Age groups
    "para",
    "paralympic",  # Para table tennis
    "vet",
    "veteran",  # Senior/ Veteran table tennis
}

# Pattern to remove u21 / u19 etc
AGE_LIMIT_PATTERN = r"\bu\d{2}\b"
# Regex to remove u21 / u19 that is not case sensitive
AGE_LIMIT_REGEX = re.compile(AGE_LIMIT_PATTERN, re.IGNORECASE)
