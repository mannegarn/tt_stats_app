import json
from src.utils.io_handler import save_raw_json, json_exists
from src.utils.helper_logic import get_event_count_from_file
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


def test_json_exists(tmp_path):
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
    assert json_exists(tmp_path, filename) is False

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(test_data, f, indent=4)

    # Where empty file exists

    assert json_exists(tmp_path, filename) is True


def test_json_exists_invalid_json_file(tmp_path):
    """
    Tests the file_exists function when the file is not a valid JSON file.

    Args:
        tmp_path (Path): The temporary directory to use for creating the file.

    Asserts:
        The function returns False when the file is not a valid JSON file.
    """
    filename = "test_file.json"
    test_data = "{This is not a valid JSON file.}"
    filepath = tmp_path / filename
    filepath.write_text(test_data)

    assert json_exists(tmp_path, filename) is False


def test_json_exists_non_json_file(tmp_path):
    """
    Tests the file_exists function when the file is not a JSON file.

    Args:
        tmp_path (Path): The temporary directory to use for creating the file.

    Asserts:
        The function returns False when the file is not a JSON file.
    """
    filename = "test_file.txt"
    test_data = "This is not a JSON file."
    filepath = tmp_path / filename
    filepath.write_text(test_data)

    assert json_exists(tmp_path, filename) is False


@pytest.mark.parametrize(
    "year_file, expected_count",
    [
        ("events_1926_count_1.json", 1),
        ("events_1927_count_0.json", 0),
        ("events_1933_count_2.json", 2),
    ],
)
def test_get_event_count_from_file(
    events_by_year_fixtures_dir, year_file, expected_count
):
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

    count = get_event_count_from_file(events_by_year_fixtures_dir, year_file)
    assert count == expected_count


@pytest.mark.parametrize(
    "year_file",
    [
        ("events_1926_count_1.json"),
        ("events_1927_count_0.json"),
        ("events_1933_count_2.json"),
    ],
)
def test_get_event_count_matches_api_response(events_by_year_fixtures_dir, year_file):
    """
    Tests the get_event_count_from_file function by parameterizing different year files
    with their expected event counts based on the internal count provided in the fixture json.
    Files are real files from API that are however not used in the analysis

    Args:
        year_file (str): The filename of the year file to test.

    Asserts:
        The function returns the same number of events as the fixture states inside its count value
    """

    function_count = get_event_count_from_file(events_by_year_fixtures_dir, year_file)
    fixture_path = events_by_year_fixtures_dir / year_file
    api_provided_count = 0

    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        api_provided_count = data[0].get("Count", 0)
    assert function_count == api_provided_count
