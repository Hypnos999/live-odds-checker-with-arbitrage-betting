import httpx
from scripts.scraping.scraper import Scraper
import asyncio
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except:
    pass

def manage_start(
    website_to_use: list[str],
    scrapers_data: dict,
) -> list[Scraper]:
    """Initialize Scrapers object"""
    scrapers: list[Scraper] = []

    ## create scrapers object
    for scraper in scrapers_data:
        if scraper not in website_to_use: continue

        scrapers.append(Scraper(
            headers=scrapers_data[scraper]['headers'],
            urls=scrapers_data[scraper]['scraper-urls'],
            name=scraper,
            provider=scrapers_data[scraper]['provider'],
            focus_url=scrapers_data[scraper]['focus-url'],
        ))
        
    return scrapers

## prepare start of new cycle, also clean each scraper variables
def manage_prep(scrapers: list[Scraper], i: int):
    for scraper in scrapers:
        scraper.prep(i)

async def manage_scrape(scrapers: list[Scraper], sport_to_use) -> None:
    """scrape data from website trough async http requests"""
    async def run():
        async with httpx.AsyncClient() as session:
            tasks = []
            for scraper in scrapers:
                for sport, url in scraper.get_urls().items():
                    if sport != 'all' and sport not in sport_to_use: continue
                    
                    tasks.append( asyncio.ensure_future(scraper.scrape(session, url)) )
            
            await asyncio.gather(*tasks)
        
    await run()
    
def manage_parse(scrapers: list[Scraper], i: int) -> dict[str: dict]:
    """Get a list of events dicts from scraped data.
events are identified and grouped by their betradar match id"""
    events = {}

    for scraper in scrapers:
        events = scraper.parse(events, i)
    
    return events
