import pytest
import asyncio
import httpx
import json
from pathlib import Path
from src.collectors.event_matches_collector import process_event_matches
from src.utils.api_client import TTStatsClient


@pytest.mark.asyncio
async def test_wtt_event_matches_api_smoke(tmp_path: Path):
    """
    # Smoke test for testing the real wtt api event matches endpoint
    Test the real endpoint of the WTT API to isolate any issues with the API if anything
    changes in the WTT API (hopefully not as this would really mess this project up but c'est la vie)
    """
    # test real WTT API using a known event with full matches data
    # Event 2550 is WTT Contender Muscat 2022 (Stable historic event)
    test_event_id = "3001"
    test_year = 2025
    stats_client = TTStatsClient()

    print(f"\n🌍 [INTEGRATION] Hitting live WTT Match API for Event {test_event_id}:")

    async with httpx.AsyncClient() as http_client:
        sem = asyncio.Semaphore(1)
        count, added = await process_event_matches(
            stats_client,
            http_client,
            test_event_id,
            test_year,
            sem,
            output_dir=tmp_path,
        )

    print(f"🌍 [INTEGRATION] Success! Received {count} matches.")

    assert count > 10
    # Note: process_event_matches creates a year sub-directory
    saved_file = tmp_path / str(test_year) / f"event_matches_{test_event_id}.json"
    assert saved_file.exists()


@pytest.mark.parametrize(
    "filename, expected_count, test_event_id, test_year",
    [
        ("event_matches_3001_fixture.json", 125, "3001", 2025),
    ],
)
@pytest.mark.asyncio
async def test_wtt_event_matches_api_regression(
    event_matches_fixtures_dir: Path,
    tmp_path: Path,
    filename: str,
    expected_count: int,
    test_event_id: str,
    test_year: int,
):
    """
    # Regression test for testing the real wtt api event matches endpoint
    Test the real endpoint of the WTT API to isolate any issues with the API if anything
    changes in the WTT API (hopefully not as this would really mess this project up but c'est la vie)

    Asserts:
        The api call returns the same number of matches as the fixture
    """

    stats_client = TTStatsClient()

    # Load expectation from fixture manually since structure differs from events
    fixture_path = event_matches_fixtures_dir / filename
    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        expected_count = len(data)

    print(f"\n🌍 [INTEGRATION] Hitting live WTT Match API for Event {test_event_id}:")

    async with httpx.AsyncClient() as http_client:
        sem = asyncio.Semaphore(1)
        count, added = await process_event_matches(
            stats_client,
            http_client,
            test_event_id,
            test_year,
            sem,
            output_dir=tmp_path,
        )

    print(f"🌍 [INTEGRATION] Success! Received {count} matches.")

    assert count == expected_count


@pytest.mark.parametrize(
    "filename, expected_count, test_event_id, test_year",
    [
        ("event_matches_3001_fixture.json", 456, "3001", 2025),
    ],
)
@pytest.mark.asyncio
async def test_wtt_event_matches_api_deep_regression(
    event_matches_fixtures_dir: Path,
    tmp_path: Path,
    filename: str,
    expected_count: int,
    test_event_id: str,
    test_year: int,
):
    """
    Deep Regression test for testing the real wtt api event matches endpoint
    Test the real endpoint of the WTT API to isolate any issues with the API if anything
    changes in the WTT API (hopefully not as this would really mess this project up but c'est la vie)

    Asserts:
        The api call returns the same json data as the fixture
    """

    stats_client = TTStatsClient()
    fixture_path = event_matches_fixtures_dir / filename
    with open(fixture_path, "r", encoding="utf-8") as f:
        expected_data = json.load(f)

    print(f"\n🌍 [INTEGRATION] Hitting live WTT Match API for Event {test_event_id}:")

    async with httpx.AsyncClient() as http_client:
        sem = asyncio.Semaphore(1)
        count, added = await process_event_matches(
            stats_client,
            http_client,
            test_event_id,
            test_year,
            sem,
            output_dir=tmp_path,
        )

    print(f"🌍 [INTEGRATION] Success! Received {count} matches.")

    saved_file = tmp_path / str(test_year) / f"event_matches_{test_event_id}.json"
    with open(saved_file, "r", encoding="utf-8") as f:
        saved_data = json.load(f)

    saved_data.sort(key=lambda x: x.get("matchId", x.get("MatchId", "")))
    expected_data.sort(key=lambda x: x.get("matchId", x.get("MatchId", "")))

    assert saved_data == expected_data
    assert count == expected_count
