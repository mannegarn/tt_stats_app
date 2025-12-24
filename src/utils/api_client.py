import httpx
import asyncio
import time 
import random
from typing import Optional, Dict, Any


class TTStatsClient:
    def __init__(self, max_pause_duration:float = 0.01):
        """
        Initialize the client
        """
        self.max_pause_duration = max_pause_duration
        self.base_headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
        }
    
    def _get_random_sleep(self):
        return random.uniform(0, self.max_pause_duration)      
        
    # SYNC / threaded section for older ITTF website
    def get_ittf_threaded(self, url: str, params: Optional[Dict] = None) -> str:
        ## blocking get request used for older ITTF website threaded calls
        
        # before call
        time.sleep(self._get_random_sleep())
        with httpx.Client(headers=self.base_headers) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                return response.text

    ## ASYNC Senction for newer API / Website

    async def post_wtt_async(self, client: httpx.AsyncClient, url: str, json_payload: Dict, headers: Optional[Dict] = None) -> Dict:
        await asyncio.sleep(self._get_random_sleep())
        
        # If content-type is in headers, remove it so httpx can add it cleanly via the json= arg
        clean_headers = headers.copy() if headers else {}
        if 'content-type' in clean_headers:
            del clean_headers['content-type']
        
        response = await client.post(url, json=json_payload, headers=clean_headers)
        response.raise_for_status()
        return response.json()

    async def get_wtt_async(self, client: httpx.AsyncClient, url: str, json_payload: Dict,params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
        # Non-blocking sleep, initialized http.x client passed in.
        # before the call to the API - do a random sleep
        # If content-type is in headers, remove it so httpx can add it cleanly via the json= arg
        clean_headers = headers.copy() if headers else {}
        if 'content-type' in clean_headers:
            del clean_headers['content-type']
        await asyncio.sleep(self._get_random_sleep())      
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

