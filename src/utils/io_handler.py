import json
from pathlib import Path
from typing import Any


def save_raw_json(data: Any, folder: Path, filename: str) -> bool:
    """
    Saves the given data as a raw JSON file in the given folder with the given filename.

    Args:
        data (Any): The data to be saved as a raw JSON file.
        folder (Path): The folder in which to save the file.
        filename (str): The filename to use for the saved file.

    Returns:
        bool: True if the file was saved successfully, False otherwise.
    """
    try:
        folder.mkdir(parents=True, exist_ok=True)

        filepath = folder / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        return True

    except Exception as e:
        print(f"❌ Error saving {filename}: {e}")
        return False


def json_exists(folder: Path, filename: str) -> bool:
    """
    Check if a file exists in a folder and is not empty and is a valid JSON file.

    Args:
        folder (Path): The folder to check in.
        filename (str): The filename to check for.

    Returns:
        bool: True if the file exists and is not empty, False otherwise.
    """
    filepath = folder / filename
    # Check if the file exists and is not empty
    if not filepath.exists() or filepath.stat().st_size == 0:
        return False
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            json.load(f)
        return True
    except (json.JSONDecodeError, IOError):
        return False


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
