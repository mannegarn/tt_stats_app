import json
from src.utils.io_handler import save_raw_json, file_exists, get_event_count_from_file
from pathlib import Path
import pytest


def test_save_raw_json(tmp_path):
    """
    Tests the save_raw_json function.

    Args:
        tmp_path (Path): The temporary directory to use for saving the file.

    Asserts:
        The file is saved successfully.
        The file exists in the given directory.
        The contents of the saved file are equal to the test data.
    """
    filename = "test_file.json"
    test_data = {"test_key": "test_value", "test_key2": "test_value2"}

    result = save_raw_json(test_data, tmp_path, filename)

    assert result is True

    saved_file = tmp_path / filename
    assert saved_file.exists()

    with saved_file.open("r", encoding="utf-8") as f:
        loaded_data = json.load(f)
        assert loaded_data == test_data


def test_file_exists(tmp_path):
    """
    Tests the file_exists function.

    Args:
        tmp_path (Path): The temporary directory to use for creating the file.

    Asserts:
        The file does not exist in the given directory initially.
        The file exists in the given directory after being created.
    """
    filename = "test_file.json"
    test_data = {"test_key": "test_value", "test_key2": "test_value2"}
    filepath = tmp_path / filename

    # Where file does not exist
    assert file_exists(tmp_path, filename) is False

    # Where empty file exists
    filepath.touch()
    assert file_exists(tmp_path, filename) is False

    filepath.write_text(json.dumps(test_data))
    assert file_exists(tmp_path, filename) is True


@pytest.mark.parametrize(
    "year_file, expected_count",
    [
        ("events_1926_count_1.json", 1),
        ("events_1927_count_0.json", 0),
        ("events_1933_count_2.json", 2),
    ],
)
def test_get_event_count_from_file(year_file, expected_count):
    """
    Tests the get_event_count_from_file function by parameterizing different year files
    with their expected event counts.
    Files are real files from API that are however not used in the analysis


    Args:
        year_file (str): The filename of the year file to test.
        expected_count (int): The expected number of events in the year file.

    Asserts:
        The function returns the correct number of events for each year file.
    """
    path = Path("tests/fixtures/events_by_year") / year_file
    count = get_event_count_from_file(path.parent, path.name)
    assert count == expected_count
