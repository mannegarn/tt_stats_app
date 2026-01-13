import pytest
import asyncio
import httpx
import json
from pathlib import Path
from src.collectors.event_collector import process_year
from src.utils.api_client import TTStatsClient
from src.utils.helper_logic import get_event_count_from_file


@pytest.mark.asyncio
async def test_wtt_api_smoke(tmp_path: Path):
    """
    # Smoke test for testing the real wtt api events endpoint
    Test the real endpoint of the WTT API to isolate any issues with the API if anything
    changes in the WTT API (hopefully not as this would really mess this project up but c'est la vie)
    """
    # test real WTT API using earliest year with full matches data
    # could test any year - even without matches data, the events endpoint still returns events.
    test_year = 2021
    stats_client = TTStatsClient()

    print(f"\n🌍 [INTEGRATION] Hitting live WTT API for year {test_year}:")

    async with httpx.AsyncClient() as http_client:
        sem = asyncio.Semaphore(1)
        count, added = await process_year(
            stats_client, http_client, test_year, sem, output_dir=tmp_path
        )

    print(f"🌍 [INTEGRATION] Success! Received {count} events.")

    assert count > 10
    saved_file = tmp_path / f"events_{test_year}.json"
    assert saved_file.exists()


@pytest.mark.parametrize(
    "filename, expected_count, test_year",
    [
        ("events_2021_count_100.json", 100, 2021),
    ],
)
@pytest.mark.asyncio
async def test_wtt_api_regression(
    events_by_year_fixtures_dir: Path,
    tmp_path: Path,
    filename: str,
    expected_count: int,
    test_year: int,
):
    """
    # Regression test for testing the real wtt api events endpoint
    Test the real endpoint of the WTT API to isolate any issues with the API if anything
    changes in the WTT API (hopefully not as this would really mess this project up but c'est la vie)

    Asserts:
        The api call returns the same number of events as the fixture
    """
    # test real WTT API using earliest year with full matches data
    # could test any year - even without matches data, the events endpoint still returns events.

    stats_client = TTStatsClient()

    expected_count = get_event_count_from_file(events_by_year_fixtures_dir, filename)

    print(f"\n🌍 [INTEGRATION] Hitting live WTT API for year {test_year}:")

    async with httpx.AsyncClient() as http_client:
        sem = asyncio.Semaphore(1)
        count, added = await process_year(
            stats_client, http_client, test_year, sem, output_dir=tmp_path
        )

    print(f"🌍 [INTEGRATION] Success! Received {count} events.")

    assert count == expected_count


@pytest.mark.parametrize(
    "filename, expected_count, test_year",
    [
        ("events_2021_count_100.json", 100, 2021),
    ],
)
@pytest.mark.asyncio
async def test_wtt_api_deep_regression(
    events_by_year_fixtures_dir: Path,
    tmp_path: Path,
    filename: str,
    expected_count: int,
    test_year: int,
):
    """
    Deep Regression test for testing the real wtt api events endpoint
    Test the real endpoint of the WTT API to isolate any issues with the API if anything
    changes in the WTT API (hopefully not as this would really mess this project up but c'est la vie)

    Asserts:
        The api call returns the same json data as the fixture
    """
    # test real WTT API using earliest year with full matches data
    # could test any year - even without matches data, the events endpoint still returns events.

    stats_client = TTStatsClient()
    fixture_path = events_by_year_fixtures_dir / filename
    with open(fixture_path, "r", encoding="utf-8") as f:
        expected_data = json.load(f)

    print(f"\n🌍 [INTEGRATION] Hitting live WTT API for year {test_year}:")

    async with httpx.AsyncClient() as http_client:
        sem = asyncio.Semaphore(1)
        count, added = await process_year(
            stats_client, http_client, test_year, sem, output_dir=tmp_path
        )

    print(f"🌍 [INTEGRATION] Success! Received {count} events.")

    saved_file = tmp_path / f"events_{test_year}.json"
    with open(saved_file, "r", encoding="utf-8") as f:
        saved_data = json.load(f)

    assert saved_data == expected_data

    assert count == expected_count
