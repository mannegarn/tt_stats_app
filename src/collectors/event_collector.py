import asyncio
import httpx
import sys
import json 
import time
from tqdm.asyncio import tqdm
from pathlib import Path



sys.path.append(".")

from src.utils.api_client import TTStatsClient
from src.utils.routes import WTTRoutes
# from src.utils.io_handler import save_raw_json, file_exists
from src.config import RAW_EVENTS_DIR

def save_file_locally(data, filename):
    """Simple saver for your POC."""
    output_path = Path("data/raw/events") / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


async def process_year(client,http_client, year, semaphore):
    ### scrapes one year using sempahore and progress bar

    async with semaphore:
        route = WTTRoutes.get_events_year_route(year)

        try:
            data = await client.post_wtt_async(
                client = http_client,
                url = route["url"],
                json_payload = route["json_payload"],
                headers = route["headers"]
            )           

            filename = f"events_{year}.json"
            save_file_locally(data, filename)

            count = 0
            if isinstance(data, list) and len(data) > 0:
                count = len(data[0].get('rows', []))              
            return count
            print(f"Obtained {count} events for {year}.")

        except Exception as e:
            tqdm.write(f"❌ Error on {year}: {e}")
            return 0    


    
async def run_event_scraper():
    # Initialize Client with default settings
    stats_client = TTStatsClient()
    start_time = time.time()
    semaphore = asyncio.Semaphore(50)
    
    print("--- 🟢 Commencing Event Scraper 🟢---")

    async with httpx.AsyncClient(timeout=30.0) as http_client:
        tasks = []
        years = range(1900, 2027)
       

        for year in years:
            task = asyncio.create_task(process_year(stats_client,http_client, year, semaphore))
            tasks.append(task)

        print(f"🚀 Launching {len(tasks)} tasks...")
        
        results = await tqdm.gather(*tasks, desc="Scraping Events", unit="year")
        
        total_events = sum([result for result in results if result is not None])
           
        elapsed = time.time() - start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        
        print(f"\n🎉 Completed {len(results)} tasks in {minutes}m {seconds}s.")
        print(f"Total events found: {total_events}")
        print("--- 🟢 Event Scraper Complete 🟢---")

async def process_year_wrapper(stats_client, http_client, year, sem):
    # Just calling the logic we defined above
    return await process_year_logic(stats_client, http_client, year, sem)

async def process_year_logic(stats_client, http_client, year, semaphore):
    async with semaphore:
        route = WTTRoutes.get_events_year_route(year)
        try:
            data = await stats_client.postwtt_async(
                client=http_client,
                url=route["url"],
                json_payload=route["json_payload"],
                headers=route["headers"]
            )
            
            save_file_locally(data, f"events_{year}.json")
            
            count = 0
            if isinstance(data, list) and len(data) > 0:
                count = len(data[0].get('rows', []))
                
            
            # print(f"   -> {year}: {count} events")
            return count
        except Exception as e:
            print(f"   ❌ {year}: {e}")
            return 0

if __name__ == "__main__":
    asyncio.run(run_event_scraper())