from fake_headers import Headers
from json import loads
from dataclasses import dataclass
import importlib
import time
import logging

@dataclass
class Scraper:
    def __init__(
        self, 
        headers: dict, 
        urls: dict[str: str],
        name: str, 
        provider: str, 
        focus_url: str, 
    ):
        self.name = name
        self.urls = urls
        self.focus_url = focus_url
        self.headers = headers
        self.event_counter = 0

        self.data: list[dict] = []
        self.error = False  
        
        if provider == 'none':
            module = importlib.import_module(f'scripts.scraping.scrapers.{name}')
        else:
            module = importlib.import_module(f'scripts.scraping.scrapers.{provider}')
        
        self.parse_func = getattr(module, 'parse')
        
        format = logging.Formatter('%(asctime)s: %(message)s')
        fileHandler = logging.FileHandler(f'files/logs/scrapers/{name}.log')
        fileHandler.setFormatter(format)
        self.logger = logging.getLogger(f'scraper-{name}')
        self.logger.addHandler(fileHandler)
        self.logger.setLevel('DEBUG')
        
        
    def get_urls(self): return self.urls
    
    def get_name(self): return self.name
    
    def get_data(self): return self.data
    
    def prep(self, i : int) -> None:
        """Clean object variables"""
        self.data = []
        self.event_counter = 0
        
        self.logger.info('')
        self.logger.info(f'Iteration n.{i}')

    async def scrape(self, session, url) -> None:
        """Scrape single url"""
        
        t = time.time()
        
        # add random User-Agent to headers that don't have it
        if 'User-Agent' not in self.headers: 
            self.headers['User-Agent'] = Headers(browser='chrome', headers=False, os='win').generate()['User-Agent']
            
        result = ''
        try:
            r = await session.get( 
                url=url, 
                headers=self.headers,
            )
            if r.status_code != 200:
                raise Exception(f'Request, code {r.status_code}')
                

            result = r.text
            if len(result) == 0: 
                self.logger.info('no data avaible')
            self.data.append(loads(result))

        except Exception as e:
            self.logger.exception(e)
            return
        
        self.logger.info(f'scrape-performance: {round(time.time() - t, 4)}')
        
    def get_data(self): return self.data
    
        
    def parse(
        self,
        events: dict[dict],
        cycle: int
    ):
        new_events = self.parse_func(self, events, cycle)
        self.logger.info(f'found n.{self.event_counter} events')
        
        return new_events 
        
    # del any odd with a value <= 1 and add the checked result to events parsed
    def check_odds_and_append (
        self,
        odds: dict,
        events: dict[dict], ## events alredy parsed
        bet_radar_id: str|int, ## event code
        cycle: str,
        info: dict[str: dict[str: str]]
    ):

        # create odds
        output = {}
        
        
        try:
            for bet_type in odds:
                for outcome in odds[bet_type]:
                    if odds[bet_type][outcome] <= 1: continue
                    if bet_type not in output: output[bet_type] = {}
                    output[bet_type][outcome] = odds[bet_type][outcome]
        except:
            self.logger.info('')
        if len(output) == 0: 
            if bet_radar_id in events: events.pop(bet_radar_id)
            return events
        
        if bet_radar_id not in events: 
            events[bet_radar_id] = {
                'bet_radar_id': bet_radar_id,
                'cycle': cycle,
                'odds': {},
                'info': {}
            }

        # add odds
        for bet_type in output:
            if bet_type not in events[bet_radar_id]['odds']: events[bet_radar_id]['odds'][bet_type] = {}
            for outcome in output[bet_type]:
                if outcome not in events[bet_radar_id]['odds'][bet_type]: events[bet_radar_id]['odds'][bet_type][outcome] = {}
                events[bet_radar_id]['odds'][bet_type][outcome][self.name] = output[bet_type][outcome]
        
        # add info
        events[bet_radar_id]['info'] |= info
        self.event_counter += 1
        
        return events
