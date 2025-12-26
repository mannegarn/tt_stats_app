import asyncio
import httpx
import sys
import time
from typing import Tuple
from datetime import datetime
from tqdm.asyncio import tqdm


sys.path.append(".")

from src.utils.api_client import TTStatsClient
from src.utils.routes import WTTRoutes
from src.utils.io_handler import save_raw_json, file_exists, get_event_count_from_file
from src.config import RAW_EVENTS_DIR


current_year = datetime.now().year

# 2021 is the earliest year where data is available from WTT API
start_year = 1926
# scrape until the year after the current year
end_year = current_year + 1
end_year = 1966

# all years = range(start_year, end_year
all_years = list(range(start_year, end_year + 1))
years_to_scrape = [
    year
    for year in all_years
    if not file_exists(filename=f"events_{year}.json", folder=RAW_EVENTS_DIR)
    or year >= current_year
]


async def process_year(client, http_client, year, semaphore) -> Tuple[int, int]:
    ### scrapes one year using sempahore and progress bar

    """
    Scrapes one year of events from the WTT API using a sempahore and progress bar.

    Args:
        client (TTStatsClient): The client to use for making requests.
        http_client (httpx.AsyncClient): The underlying HTTP client.
        year (int): The year to scrape.
        semaphore (asyncio.Semaphore): The sempahore to use for limiting concurrent requests.

    Returns:
        Tuple[int, int]: A tuple containing the total number of events found and the number of new events added.
    """
    async with semaphore:
        route = WTTRoutes.get_events_year_route(year)

        try:

            filename = f"events_{year}.json"
            old_count = get_event_count_from_file(RAW_EVENTS_DIR, filename)

            data = await client.post_wtt_async(
                client=http_client,
                url=route["url"],
                json_payload=route["json_payload"],
                headers=route["headers"],
            )

            filename = f"events_{year}.json"
            save_raw_json(data, RAW_EVENTS_DIR, filename)

            new_count = 0
            if isinstance(data, list) and len(data) > 0:
                new_count = len(data[0].get("rows", []))

            added = new_count - old_count
            if added > 0:
                status = "New file" if old_count == 0 else f"{added} new events"
                tqdm.write(f"🟢 {year}: {status} (Total: {new_count})")

            return new_count, added

        except Exception as e:
            tqdm.write(f"❌ Error on {year}: {e}")
            return 0


async def run_event_scraper() -> None:
    """
    Runs the event scraper which scrapes all available event data from the WTT API.

    This function initializes a TTStatsClient with default settings, then launches
    tasks to scrape each year of events from the WTT API. Each task is bounded
    by a semaphore to limit the number of concurrent requests. The function
    then gathers all the tasks and prints out the total number of events found,
    the number of new events found, and the total time taken to complete the
    scraping.

    Returns:
        None
    """

    # Initialize Client with default settings
    stats_client = TTStatsClient()
    start_time = time.time()
    semaphore = asyncio.Semaphore(50)

    print("--- 🟢 Commencing Event Scraper 🟢---")

    async with httpx.AsyncClient(timeout=30.0) as http_client:
        tasks = []
        years = years_to_scrape

        for year in years:
            task = asyncio.create_task(
                process_year(stats_client, http_client, year, semaphore)
            )
            tasks.append(task)

        print(f"🚀 Launching {len(tasks)} tasks...")

        results = await tqdm.gather(*tasks, desc="Scraping Events", unit="year")

        total_events = sum([result[0] for result in results if result is not None])
        new_events = sum([result[1] for result in results if result is not None])

        elapsed = time.time() - start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)

        print(f"\n🎉 Completed {len(results)} tasks in {minutes}m {seconds}s.")
        print(f"Total events found: {total_events}")
        print(f"New events found: {new_events}")
        print("--- 🟢 Event Scraper Complete 🟢---")


if __name__ == "__main__":
    asyncio.run(run_event_scraper())
