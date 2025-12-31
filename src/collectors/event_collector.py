import asyncio
import httpx
import time
from typing import Tuple
from datetime import datetime
from tqdm.asyncio import tqdm
from pathlib import Path


from src.utils.api_client import TTStatsClient
from src.utils.routes import WTTRoutes
from src.utils.io_handler import save_raw_json, json_exists, get_event_count_from_file
from src.config import RAW_EVENTS_DIR


def get_years_to_scrape(output_dir: Path, start_yr: int = 2021) -> list[int]:
    """
    Determines which years to scrape based on existing data and the current year.
    """
    current_year = datetime.now().year
    # end_year is current + 2 to see future events out of interest.
    all_years = range(start_yr, current_year + 2)

    years_to_scrape = []
    for year in all_years:
        filename = f"events_{year}.json"

        if not json_exists(output_dir, filename) or year >= current_year:
            years_to_scrape.append(year)

    return years_to_scrape


async def process_year(
    client: TTStatsClient,
    http_client: httpx.AsyncClient,
    year: int,
    semaphore: asyncio.Semaphore,
    output_dir: Path = RAW_EVENTS_DIR,
) -> Tuple[int, int]:
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
            old_count = get_event_count_from_file(output_dir, filename)

            data = await client.post_wtt_async(
                client=http_client,
                url=route["url"],
                json_payload=route["json_payload"],
                headers=route["headers"],
            )

            filename = f"events_{year}.json"
            save_raw_json(data, output_dir, filename)

            new_count = 0
            if isinstance(data, list) and len(data) > 0:
                new_count = len(data[0].get("rows", []))

            added = max(0, new_count - old_count)
            if added > 0:
                status = "New file" if old_count == 0 else f"{added} new events"
                tqdm.write(f"🟢 {year}: {status} (Total: {new_count})")

            return new_count, added

        except Exception as e:
            tqdm.write(f"❌ Error on {year}: {e}")
            return 0, 0


async def run_event_scraper(years_to_scrape: list[int]) -> None:
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
    years_to_scrape = get_years_to_scrape(output_dir=RAW_EVENTS_DIR)
    asyncio.run(run_event_scraper(years_to_scrape))
