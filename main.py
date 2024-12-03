from scraping.utils import manage_start, manage_prep, manage_scrape, manage_parse
from arbitrage.event import Event
from arbitrage.arb import Arb
from config import Config

import time
import json
import glob
import os
import logging
import shutil
import asyncio

try:
    import uvloop
except:
    pass


async def main(app_runner: str):
    ## clean log files
    files = glob.glob(os.path.join('files/logs', '*'))
    for f in files:
        try:
            os.remove(f)
        except:
            shutil.rmtree(f)

    path = os.path.join('files/logs', 'bots')
    os.mkdir(path)

    path = os.path.join('files/logs', 'scrapers')
    os.mkdir(path)

    ## logger setup
    f = logging.Formatter("%(asctime)s: %(message)s")
    file_info = logging.FileHandler('files/logs/main.log', mode="a")
    file_info.setFormatter(f)

    cmd_info = logging.StreamHandler()
    cmd_info.setFormatter(f)
    logger = logging.getLogger('log')
    logger.setLevel('DEBUG')
    logger.addHandler(file_info)
    logger.addHandler(cmd_info)
    logger.info(f'Started application with {app_runner}')

    ## load files & config
    config = Config()
    with open(config.data_path, 'r') as f:
        data = json.loads(f.read())

    logger.info('Loaded needed files and cleaned logs')
    logger.info(f'Config: \n{json.dumps(config.to_json(), indent=2)}\n')

    scrapers = manage_start(
        scrapers_data=data,
        website_to_use=config.website_to_use,
    )
    logger.info(f'Created scrapers for: {", ".join(config.website_to_use)}')

    logger.info("Starting main loop, press CTRL + C to exit")
    i = 0

    while True:
        logger.info('')
        logger.info(f'Iteration n.{i}')

        ## scraping & parsing
        scrapers_t = time.time()
        manage_prep(scrapers, i)
        await manage_scrape(scrapers, config.sport_to_use)
        events_dict = manage_parse(scrapers, i)
        logger.info(f"Scraping and parsing done in {round(time.time() - scrapers_t, 4)}s")

        ## odds/arbitrage analysis
        events = list(
            map(
                lambda x: Event(
                    **x,
                    sport_to_use=config.sport_to_use,
                ),
                events_dict.values()
            )
        )

        if events:
            with open(config.events_path, 'w') as f:
                f.write(json.dumps([e.to_dict() for e in events], indent=2))

            odds = {e.bet_radar_id: e.odds for e in events}
            with open(config.odds_path, 'w') as f:
                f.write(json.dumps(odds, indent=2))

            info = {e.bet_radar_id: e.info for e in events}
            with open(config.info_path, 'w') as f:
                f.write(json.dumps(info, indent=2))

            events_by_sport = {}
            for event in events:
                if event.sport not in events_by_sport: events_by_sport[event.sport] = []
                events_by_sport[event.sport].append(event.to_dict())
            with open(config.events_by_sport_path, 'w') as f:
                f.write(json.dumps(events_by_sport, indent=2))

        arbs: dict[str, Arb] = {
            arb.score: arb
            for arb_list in map(
                lambda event: Arb.get_arbs(
                    event,
                    total_amount=config.total_amount,
                    bet_round_up=config.bet_round_up
                ),
                events) for arb in arb_list if arb.get_status() # or True  # TODO: comment
        }

        if arbs:
            with open(config.arbs_path, 'w') as f:
                f.write(json.dumps([a.get_format() for a in list(arbs.values())], indent=2))

        logger.info(f"Found: n.{len(events)} events, n.{len(arbs)} arbs")


        # sleep betwheen iterations
        if config.sleep_after_run > 0: 
            time.sleep(config.sleep_after_run)

        i += 1

if __name__ == "__main__":
    uvloop_runner = True
    try:
        try:
            uvloop.run(main('uvloop'))
        except NameError:
            uvloop_runner = False
        
        if not uvloop_runner:
            asyncio.run(main('asyncio'))
    except KeyboardInterrupt:
        print('')
        print("Exiting programm...")