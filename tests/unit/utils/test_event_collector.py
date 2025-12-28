import pytest
import respx
import httpx
import asyncio
import json
from pathlib import Path
from src.collectors.event_collector import process_year
from src.utils.api_client import TTStatsClient


@pytest.mark.parametrize(
    "filename, expected_count, test_year",
    [
        ("events_1926_count_1.json", 1, 1926),
        ("events_1927_count_0.json", 0, 1927),
        ("events_1933_count_2.json", 2, 1933),
    ],
)
@pytest.mark.asyncio
async def test_process_year(
    stats_client: TTStatsClient,
    wtt_api_mock: respx.Router,
    tmp_path: Path,
    events_by_year_fixtures_dir: Path,
    filename: str,
    expected_count: int,
    test_year: int,
):
    """
    Test the process_year function with mocked responses from the WTT API.
    The responses are real responses from the WTT API that are however not used in the analysis
    Found in the test/fixtures/events_by_year folder
    Pretend the API returns a list of events for a given year.
    Assert that the function returns the correct number of events found and the number of new events added,
    and saves the events to a file.

    Args:
        stats_client (TTStatsClient): A TTStatsClient instance.
        wtt_api_mock (respx.MockRouter): A mocked router for the WTT API."""

    assert events_by_year_fixtures_dir.exists()
    with open(events_by_year_fixtures_dir / filename, "r", encoding="utf-8") as f:
        real_data = json.load(f)

    # need catch any request that ends with /api/eventcalendar - and return the real data
    # This caused lots of issues - but appears to be working
    # This will need to be checked when adapting this test to other modules.
    wtt_api_mock.post(url__regex=r".*/api/.*").mock(
        return_value=httpx.Response(200, json=real_data)
    )

    ###### run the mock API

    async with httpx.AsyncClient(timeout=30.0) as http_client:
        sem = asyncio.Semaphore(10)

        count, added = await process_year(
            stats_client, http_client, test_year, sem, output_dir=tmp_path
        )

    assert count == expected_count
    assert added == expected_count

    saved_file = tmp_path / f"events_{test_year}.json"
    assert saved_file.exists()

    with saved_file.open("r", encoding="utf-8") as f:
        loaded_data = json.load(f)
        assert loaded_data == real_data

    saved_data = json.load(saved_file.open("r", encoding="utf-8"))
    assert saved_data == real_data
