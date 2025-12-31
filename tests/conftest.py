import pytest
import respx
from pathlib import Path
from src.utils.api_client import TTStatsClient


@pytest.fixture
def fixtures_dir():
    """
    Returns the path to the fixtures directory.
    """
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def events_by_year_fixtures_dir(fixtures_dir):
    """
    Returns the path to the events fixtures directory.
    """
    return fixtures_dir / "events_by_year"


@pytest.fixture
def stats_client():
    """
    Returns a TTStatsClient instance.
    """
    return TTStatsClient(max_pause_duration=0.01)


@pytest.fixture
def wtt_api_mock():
    """
    Returns a mocked version of the WTT API client.
    Using respx for wtt_api_mock.post() etc
     !!! When refactoring DOUBLE check this is working !!!
    """
    with respx.mock(assert_all_called=False) as mock:
        yield mock


@pytest.fixture
def event_matches_fixtures_dir(fixtures_dir: Path) -> Path:
    """Returns the path to the event_matches fixtures subdirectory."""
    return fixtures_dir / "event_matches"
