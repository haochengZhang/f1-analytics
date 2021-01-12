from bs4 import BeautifulSoup

import pandas as pd

import requests


class Season:
    
    def __init__(self, year):
        self.year = year

        self.get_season_data()

        self.drivers = {}
        self.constructors = {}
        self.points = {'':0}

    def get_season_data(self):
        # Gets (round, racename) tuple for the given season

        payload = f"http://ergast.com/api/f1/{self.year}"

        r = requests.get(payload)
        if r.status_code != 200:
            raise RuntimeError("API Call Failed")
        
        soup = BeautifulSoup(r.text).mrdata
        self.round_count = soup.get('total')

        self.racename = {}
        for race in soup.find_all('race'):
            round = int(race.get('round'))
            racename = race.racename.contents[0]
            self.racename[round] = racename

    def create_race(self, round):
        # Creates a Race object stored in races[round]
        self.races = {round:Race(self.year, round, self.racename[round])}


class Race():

    def __init__(self, year, round, name):
        self.year = year
        self.round = round
        self.name = name
        
    def api_call(self, query, limit=30, offset=0):
        payload = (
            f"http://ergast.com/api/f1/{self.year}/{self.round}/"
            f"{query}?limit={limit}&offset={offset}"
            )

        r = requests.get(payload)
        if r.status_code != 200:
            raise RuntimeError("API Call Failed")
        return BeautifulSoup(r.text)

    def get_timing_data(self):
        # Gets timing data and creates a df containing each
        # (driver,laptime,constructor) for all laps

        soup = self.api_call('laps', limit=1000)
        totalRows = int(soup.mrdata.get('total'))
        self.df_timing = pd.DataFrame(
                columns=['Driver', 'Lap', 'Position', 'LapTime'])

        # First loop checks if we have all laps of given race
        while len(self.df_timing.index) < totalRows:
            # Iter over each (driver,lap) 
            for driver in soup.find_all('timing'):
                name = driver.get('driverid')
                lap = driver.get('lap')
                pos = driver.get('position')
                time = driver.get('time')
                time = time.replace(':', ' min ') + ' sec'
                time = pd.to_timedelta(time)

                self.df_timing = self.df_timing.append({
                            'Driver':name,'Lap':lap,
                            'Position':pos, 'LapTime':time
                        }, ignore_index=True)
                        
            if len(self.df_timing.index) >= totalRows:
                break

            soup = self.api_call(
                    'laps', limit=1000, offset=len(self.df_timing.index)
                    )
        # Convert laptime from timedelta to min for plotting in seaborn
        self.df_timing.LapTime = pd.to_numeric(
                pd.Series(self.df_timing.LapTime))/6e10 #ns to min

        # Grabs constructor,driver info
        soup = self.api_call('results')
        df_driverinfo = pd.DataFrame(columns=['Driver', 'Constructor'])

        for result in soup.find_all('result'):
            constructor = result.constructor.get('constructorid')
            driver = result.driver.get('driverid')
            df_driverinfo = df_driverinfo.append({
                    'Driver':driver,
                    'Constructor':constructor
                    }, ignore_index=True)

        # Joins constructor info to timing dataframe
        self.df_timing = self.df_timing.join(
                df_driverinfo.set_index('Driver'), on='Driver')

    def format_by_driver(self):
        # Formats new df with driver as column, laptime as row
        self.df_timing_byDriver = pd.DataFrame(
                data=self.df_timing.Lap.unique(),columns=['Lap'])

        for driver in self.df_timing['Driver'].unique():
            # PD Series of laptime for each driver with index as lap
            right = self.df_timing[
                    ['Driver', 'LapTime', 'Lap']
                    ].loc[self.df_timing['Driver'] == driver].set_index(
                            'Lap')['LapTime']
            right.name = driver
            self.df_timing_byDriver = self.df_timing_byDriver.join(
                    right, how='outer', on='Lap')

        self.df_timing_byDriver = self.df_timing_byDriver.set_index('Lap')
