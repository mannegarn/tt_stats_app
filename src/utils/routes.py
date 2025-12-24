import json 




class WTTRoutes:
    # Use exact headers from CUrl copy.
    _BASE_HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-GB,en;q=0.9,es;q=0.8',
    'cache-control': 'no-cache',
    'content-type': 'application/json',
    'dnt': '1',
    'origin': 'https://www.worldtabletennis.com',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://www.worldtabletennis.com/',
    'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',       
    'secapimkey': 'S_WTT_882jjh7basdj91834783mds8j2jsd81', 
    'user-agent': 'Mozilla/5.0 (Linux; Android 11.0; Surface Duo) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36'
    }

    @staticmethod
    def get_events_year_route(year: int):
        # returns the method, url, and payload and headers to fetch the events for a given year range
        # found upon inspecting the WTT API request on this calendar page :
        # https://www.worldtabletennis.com/events_calendar

        url = "https://wtt-website-api-prod-3-frontdoor-bddnb2haduafdze9.a01.azurefd.net/api/eventcalendar" 

        inner_filter = [
            {"name": "StartDateTime", "value": year, "custom_handling": "multimatch_year_or_filter", "condition": "or_start"},
            {"name": "FromStartDate", "value": year, "custom_handling": "multimatch_year_or_filter", "condition": "or_end"}
        ]

        payload = {
            "custom_filter": json.dumps(inner_filter)
        }

        return {
            "method": "POST",
            "url": url,
            "json_payload": payload,  # Note: we use 'json_payload' to match our client arg
            "headers": WTTRoutes._BASE_HEADERS
        }