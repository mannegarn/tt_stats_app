# src/config.py
from pathlib import Path

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

# Ensure ALL directories exist when config is imported
for directory in [RAW_EVENTS_DIR, RAW_MATCHES_DIR, RAW_PLAYERS_DIR, INTERMEDIATE_DIR, MASTER_DIR]:
    directory.mkdir(parents=True, exist_ok=True)