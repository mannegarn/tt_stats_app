import asyncio
import httpx
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple
from tqdm.asyncio import tqdm
import time
from typing import Union
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from src.config import RAW_EVENTS_DIR, RAW_EVENT_MATCHES_DIR
from src.utils.api_client import TTStatsClient
from src.utils.routes import WTTRoutes
from src.utils.io_handler import save_raw_json, json_exists


# Get the current year and date
# Use an offset of 1 day for safe current date to account for potential timezone differences
# The date is used to filter ongoing events that need to be re-scraped
current_year = datetime.now().year
current_date = datetime.now()
ongoing_cut_off_date = current_date + timedelta(days=1)


def get_event_matches_to_scrape(
    events_dir: Path,
    event_matches_dir: Path,
    current_year: int,
    ongoing_cut_off_date: datetime,
) -> List[Tuple[int, int]]:
    """
    1. Get all events from the events directory
    2. Get all event matches directories from the event matches directory
    3. Compare the two lists to determine which events need to be re-scraped or scraped
     - based on the current year and ongoing cut off date and if the data is already present
     Args:
        events_dir (Path): The directory containing the event data.
        event_matches_dir (Path): The directory containing the event match data.
        current_year (int): The current year.
        ongoing_cut_off_date (datetime): The cut-off date for ongoing events.
    Returns:
        List[Tuple[int, int]]: A list of event IDs and match IDs that need to be re-scraped.
    """
    events_to_scrape = []
    event_files = sorted(events_dir.glob("events_*.json"))

    # Iterate over the event files
    # [CHECK] if name structure changes, this can BREAK !!!

    # 1) Get all events from the events directory
    for event_file in event_files:
        try:
            year = int(event_file.stem.split("_")[1])
        except (IndexError, ValueError):
            continue

        # open and read the file for id, and EndDate
        with open(event_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # unpack the data from the api response structure
        if isinstance(data, list) and len(data) > 0:
            events_list = data[0].get("rows", [])

        for event in events_list:
            event_id = event.get("EventId")
            end_date = event.get("EndDateTime")
            if not event_id or not end_date:
                continue

            target_dir = event_matches_dir / str(year)
            target_file = target_dir / f"event_matches_{event_id}.json"

            # CASE 1) File does not exist, should scrape!
            should_scrape = False
            if year > current_year:
                should_scrape = False
            else:
                if not target_file.exists():
                    should_scrape = True

                # CASE 2)
                else:
                    end_date_safe = datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S")
                    if end_date_safe >= ongoing_cut_off_date:
                        should_scrape = True

                if should_scrape:
                    events_to_scrape.append((event_id, year))

    return events_to_scrape


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
    reraise=True,
)
async def fetch_with_retry(
    http_client: httpx.AsyncClient, route: WTTRoutes
) -> httpx.Response:
    response = await http_client.get(
        route["url"], params=route["params"], headers=route["headers"], timeout=30.0
    )
    return response


async def process_event_matches(
    client: TTStatsClient,
    http_client: httpx.AsyncClient,
    event_id: Union[int, str],
    year: int,
    semaphore: asyncio.Semaphore,
    output_dir: Path = RAW_EVENT_MATCHES_DIR,
) -> Tuple[int, int]:
    ### scrapes one year using sempahore and progress bar

    """
    Scrapes one event from the WTT API using a sempahore and progress bar
    Obtains the event_mathches payloads.
    Saves each event match to a file inside a year sub-directory inside the RAW_EVENT_MATCHES_DIR

    Args:
        client (TTStatsClient): The client to use for making requests.
        http_client (httpx.AsyncClient): The underlying HTTP client.
        year (int): The year to scrape.
        semaphore (asyncio.Semaphore): The sempahore to use for limiting concurrent requests.

    Returns:
        Tupl[int, int]: A tuple containing the total number of matches found and the number of new matches added.
    """

    # firstly check if the directory exists, if not, create it
    target_dir = output_dir / str(year)
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = f"event_matches_{event_id}.json"

    async with semaphore:
        route = WTTRoutes.get_event_matches_route(str(event_id))

        try:
            old_count = 0
            if json_exists(target_dir, filename):
                with open(target_dir / filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    old_count = len(data)

            response = await fetch_with_retry(http_client, route)
            response.raise_for_status()
            data = response.json()

            # placeholder for the count and added count
            count = len(data)
            added = count - old_count

            # save the data to a file
            save_raw_json(data, target_dir, filename)

            # update the count and added count
            ## add code here later ##

            return count, added

        except Exception as e:
            tqdm.write(f"❌ Error scraping Event {event_id}: {e}")
            return 0, 0


async def run_event_matches_scraper() -> None:
    """
    Runs the event matches scraper which scrapes all available event matches data from the WTT API.
    Args:
        None
    Returns:
        None
    """
    # Initialize Client with default settings

    print("--- 🟢 Commencing Event Match Scraper 🟢 ---")

    # Initialize
    stats_client = TTStatsClient()
    start_time = time.time()
    semaphore = asyncio.Semaphore(50)

    # 1. Get the list of work to do
    print("Scanning files for work...")
    events_to_scrape = get_event_matches_to_scrape(
        events_dir=RAW_EVENTS_DIR,
        event_matches_dir=RAW_EVENT_MATCHES_DIR,
        ongoing_cut_off_date=ongoing_cut_off_date,
        current_year=current_year,
    )

    print(f"Found {len(events_to_scrape)} events to process.")

    async with httpx.AsyncClient(timeout=30.0) as http_client:
        tasks = []

        # 2. Create Tasks
        # Loop through the DATA (event_id, year), not the empty task list
        for event_id, year in events_to_scrape:
            task = process_event_matches(
                stats_client, http_client, event_id, year, semaphore
            )
            tasks.append(task)

        if not tasks:
            print("No tasks to run.")
            return

        # 3. Run Tasks
        # Only await ONCE. wrapping in tqdm automatically awaits.
        results = await tqdm.gather(*tasks, desc="Scraping Matches", unit="event")

        # 4. Summary
        total_matches = sum(r[0] for r in results)
        new_matches = sum(r[1] for r in results)

        elapsed = time.time() - start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)

        print(f"\n🎉 Completed {len(results)} events in {minutes}m {seconds}s.")
        print(f"Total matches found: {total_matches}")
        print(f"New matches added: {new_matches}")
        print("--- 🟢 Match Scraper Complete 🟢 ---")


if __name__ == "__main__":
    asyncio.run(run_event_matches_scraper())
