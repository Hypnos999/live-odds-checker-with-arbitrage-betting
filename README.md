# live-odds-checker-with-arbitrage-betting
A  python script that scrapes betting websites APIs in real time to gather live events data and find arbitrage betting opportunities



## Supported websites
1. Sisal
2. AllInBet
3. Better
4. Eurobet
5. VinciTu
6. PlayMatika
   


## Supported sports and bets:
- football: 1X2, DC, GG/NG
- basketball: T/T, P/D
- tennis: T/T



## Data scraped about matches:
- odds
- sport (eg: "football")
- match name (eg: "Inter - Juventus")
- tournament (eg: "Serie A")
- start date and time
- running time
- score



## Functions and purposes:
1. scraping sport betting websites' APIs to gather events data
2. match events between different providers, creating also a new set of odds which are the highest ones found for each event
3. check for arbitrage opportunities


This whole process run infinitely in a loop



## Output:
The results of each iteration of this loop will be written in the output folder, in particular the files you'll find are:
1. events.json --> all the raw events dictionaries, which contains info, odds and highest_odds  for each singular event  
2. arbs.json --> all the arbs found (if there are)
3. odds.json --> a dictionary where the key is events bet_radar_ids and the value is their odds
4. info.json --> a dictionary where the key is events bet_radar_ids and the value is their info
4. events_by_sport.json --> a dictionary where the key is the sport name and the value is a list of all the events for that sport
   
I uploaded both the files in the output folder and the script logs in files/logs so that you can have a look at an example run.


## How to:
1. clone the github repo
2. create a venv & activate it
3. run pip install -r requirements.txt
4. set script behavior by changing config.py
5. run python main.py



## Disclaimer
Since i didn't implement a proxy you will be sending requests with your own IP, pay attention to not having the value of config.sleep_after_run set too low or running the script for too long. 
As websites could temporarily limit your IP (you can see that in the scrapers logs in files/logs/scrapers/, it will tell you that the response return a 403 code, look at eurobet.log for example)
