import pytest
import respx
import httpx
import asyncio
import json
from pathlib import Path
from src.collectors.event_collector import process_year, get_years_to_scrape
from src.utils.api_client import TTStatsClient
from src.config import RAW_EVENTS_DIR
from datetime import datetime


def test_get_years_to_scrape():
    """
    Tests the get_years_to_scrape function by asserting that the
    years returned range matches the expected range from 2021 to the current year plus 2.
    Args:
        None
    Asserts:
        The function returns a list of years from 2021 to the current year plus 2.
    """
    years_to_scrape = get_years_to_scrape(RAW_EVENTS_DIR)
    assert years_to_scrape == range(2021, datetime.now().year + 2)


@pytest.mark.parametrize(
    "filename, expected_count, test_year",
    [
        ("events_1926_count_1.json", 1, 1926),
        ("events_1927_count_0.json", 0, 1927),
        ("events_1933_count_2.json", 2, 1933),
    ],
)
@pytest.mark.asyncio
async def test_process_year_handles_good_response(
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
        wtt_api_mock (respx.MockRouter): A mocked router for the WTT API.
    Asserts:
        The function returns the correct number of events found and the number of new events added,
        and saves the events to a file.
    """

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

    async with httpx.AsyncClient() as http_client:
        sem = asyncio.Semaphore(1)

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


@pytest.mark.parametrize(
    "status_code, error_message",
    [
        (404, "Not Found"),
        (500, "Internal Server Error"),
        (502, "Bad Gateway"),
        (503, "Service Unavailable"),
        (504, "Gateway Timeout"),
    ],
)
@pytest.mark.asyncio
async def test_process_year_handles_bad_response(
    stats_client: TTStatsClient,
    wtt_api_mock: respx.MockRouter,
    tmp_path: Path,
    status_code: int,
    error_message: str,
):
    """
    Test the process_year function with mocked bad responses from the WTT API.
    Tests that responses 404, 500 etc are handled correctly without crashing
    It should return count, added = 0,0 and NOT save a file
    Args:
        None
    Asserts:
        Asserts that the function returns 0,0
    """
    # add dummy year - does not matter
    year = 2025

    # Mock a server eror (500 response)
    wtt_api_mock.post(url__regex=r".*/api/.*").mock(
        return_value=httpx.Response(status_code, json={"error": f"{error_message}"})
    )

    async with httpx.AsyncClient() as http_client:
        sem = asyncio.Semaphore(1)

        count, added = await process_year(
            stats_client, http_client, year, sem, output_dir=tmp_path
        )

    assert count == 0
    assert added == 0
    excepted_file = tmp_path / f"events_{year}.json"
    assert not excepted_file.exists()
