class Config():
    """config class, store all settings"""
    def __init__(self):
        self.data_path = "files/data.json"
        self.arbs_path = 'output/arbs.json'
        self.events_path = "output/events.json"
        self.events_by_sport_path = "output/events_by_sport.json"
        self.odds_path = "output/odds.json"
        self.info_path = "output/info.json"

        self.sport_to_use = ['tennis', 'football', "basketball"]
        self.website_to_use = [
            'allinbet',
            'better',
            'sisal',
            'eurobet',
            'vincitu',
            'playmatika',
        ]
        
        self.total_amount = 100 ## general amount to bet, it can vries due to round up of the bet
        self.bet_round_up = 5 ## the nearest digit to which bets stakes will be rounded
        self.sleep_after_run = 5

    def to_json(self):
        json = {}
        for attr in self.__dict__:
            json[attr] = self.__dict__[attr]
        
        return json