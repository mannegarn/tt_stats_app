import json
from src.utils.io_handler import save_raw_json


def test_save_raw_json_creates_file(tmp_path):

    test_data = {"test_key": "test_value", "test_key2": "test_value2"}
    filename = "test_file.json"

    result = save_raw_json(test_data, tmp_path, filename)

    assert result is True

    saved_file = tmp_path / filename
    assert saved_file.exists()

    with saved_file.open("r", encoding="utf-8") as f:
        loaded_data = json.load(f)
        assert loaded_data == test_data
