import pytest
from datetime import datetime, timedelta
from src.utils.helper_logic import get_event_date_status, is_senior_event


@pytest.mark.parametrize(
    "start_offset, end_offset, expected",
    [
        (5, 10, "future"),  # future: 5 days from now
        (-2, 2, "ongoing"),  # ongoing: finishes in 2 days
        (-10, -5, "completed"),  # completed: finished 5 days ago
    ],
)
def test_get_event_status_result(start_offset, end_offset, expected):
    """
    Tests the get_event_date_status function by providing different start and end dates and
    their corresponding expected statuses.

    Parameters:
        start_offset (int): The number of days from now that the event starts.
        end_offset (int): The number of days from now that the event ends.
        expected (str): The expected status of the event ("future", "ongoing", or "completed").

    Asserts:
        The function returns the expected status for the given start and end dates.
    """
    now = datetime.now()
    event_json = {
        "StartDateTime": (now + timedelta(days=start_offset)).strftime(
            "%Y-%m-%dT%H:%M:%S"
        ),
        "EndDateTime": (now + timedelta(days=end_offset)).strftime("%Y-%m-%dT%H:%M:%S"),
    }

    assert get_event_date_status(event_json) == expected


@pytest.mark.parametrize(
    "name, expected",
    [
        ("WTT Star Contender Bangkok", True),
        ("WTT Youth Contender Berlin", False),
        ("U19 Boys Singles", False),
        (None, False),
        ("", False),
    ],
)
def test_is_senior_event_result(name, expected):
    """
    Test that is_senior_event returns the correct result for different input event names

    Parameters:
        name (str): The name of the event to check
        expected (bool): The expected result of is_senior_event(name)

    Asserts:
        The function returns the expected result for the given event name
    """

    assert is_senior_event(name) == expected
