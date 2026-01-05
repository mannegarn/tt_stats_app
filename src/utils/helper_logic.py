from pathlib import Path
import json
from datetime import datetime, timedelta
from typing import Literal, Optional
import re
from src.config import EXCLUDED_EVENT_TERMS, AGE_LIMIT_REGEX


def get_event_count_from_file(folder: Path, filename: str) -> int:
    """
    Reads a raw JSON EVENTS file and returns the number of events (rows) found.

    This function is used to determine the number of events stored in a raw JSON file.
    The function takes a folder and a filename as arguments and returns the number of events found.

    Args:
        folder (Path): The folder to read the file from.
        filename (str): The filename of the file to read.

    Returns:
        int: The number of events found in the file.
    """
    filepath = folder / filename
    if not filepath.exists():
        return 0
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            # WTT api response structure is nested: list[0] -> 'rows' list
            if isinstance(data, list) and len(data) > 0:
                # Get the number of events from the 'rows' list
                return len(data[0].get("rows", []))
    except Exception:
        # If an exception occurs, return 0
        return 0
    return 0


EventStatus = Literal["future", "ongoing", "completed"]


def get_event_date_status(event_json: dict) -> Optional[EventStatus]:
    """
    Returns the date status of an event as a string.
    cases:
        - "future"
        - "ongoing"
        - "completed"

    Args:
        event_json (dict): A dictionary representing the event data.

    Returns:
        str: A string representing the status of the event.
    """

    current_date = datetime.now()
    ongoing_cut_off_date = current_date + timedelta(days=1)

    try:
        start_date_str = event_json.get("StartDateTime")
        end_date_str = event_json.get("EndDateTime")

        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%dT%H:%M:%S")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%dT%H:%M:%S")
            current_date = datetime.now()

            if start_date > ongoing_cut_off_date:
                return "future"
            elif end_date < current_date:
                return "completed"
            else:
                return "ongoing"
        else:
            return None
    except (ValueError, TypeError):
        return None


def is_senior_event(event_name: str) -> bool:
    """
    Checks if an event name is a senior event.

    The function takes an event name, converts it to lowercase, and checks
    if any of the excluded event terms are present. If not, it checks if the
    event name matches the age limit regex. If it does not match, the
    function returns True, indicating that the event is a senior event.

    Args:
        event_name (str): The name of the event to check.

    Returns:
        bool: True if the event is a senior event, False otherwise.
    """
    if not event_name:
        return False

    name_lower = event_name.lower()
    if any(term in name_lower for term in EXCLUDED_EVENT_TERMS):
        return False
    # regex match for age limit gives True that is not a senior event
    # return not the bool to get the opposite result
    return not bool(re.search(AGE_LIMIT_REGEX, name_lower))
    # Total filtered out (Youth/Junior)
