from datetime import datetime
import statistics
from typing import List

import os
import json

store_path = os.getcwd()

class PersistentStore:
    """Provides persistent storage for values that should be persisted over long
    periods of time
    """
    
    def __init__(self, name: str, data_var: str):
        self.file_name = os.path.join(store_path, f"{name}.json")
        self.data_var = data_var


    
    def _load(self):
        if not os.path.exists(self.file_name):
            return

        with open(self.file_name, 'r') as store:
            print(f'Loading {self.data_var}')
            self.__setattr__(self.data_var, json.load(store.read()))

    def _store(self):
        # with open(self.file_name, 'w') as store:
        #     print(f'Storing {self.data_var}')
        #     print(self.__getattribute__(self.data_var))
        #     store.write(json.dumps(self.__getattribute__(self.data_var), default=lambda o: o.__dict__))
        pass

class WindEvent:
    def __init__(self, speed_km: float, start_time: datetime):
        self.speed_km = speed_km
        self.start_time = start_time
    
    def toJSON(self):
        return json.dumps({ 'speed_km': self.speed_km, 'start_time': self.start_time })

class WindTracker(PersistentStore):
    wind_events: List[WindEvent] = []
    distance_per_event: float = 7 / 6 # meters
    """The distance (in meters) traveled when there is one event"""

    def __init__(self):
        super().__init__('wind_tracker', 'wind_events')

    def clean_up(self):
        max_age_minutes = 10
        max_age_seconds = max_age_minutes * 60

        self.wind_events = list(filter(lambda event: (datetime.now() - event.start_time).seconds < max_age_seconds, self.wind_events))
        self._store()

    def add_event(self, time: datetime):
        self.clean_up()

        if len(self.wind_events) == 0: 
            self.wind_events.append(WindEvent(0, time))
            return

        last_time = self.wind_events[-1].start_time
        dif = time - last_time
        dif_seconds = dif.seconds + dif.microseconds / 1000000 # Note that if the time was less than one second, the dif will be zero, so we need to calculate the microseconds
        speed_mps = self.distance_per_event / dif_seconds # Wind speed in m/s
        speed_kph = speed_mps / 1000 * 60 * 60

        if speed_kph > 1000:
            # THis only happens when there is a double bounce, so we should 
            # try to filter it out
            return

        print(f"Wind Speed: {speed_kph}")

        self.wind_events.append(WindEvent(speed_kph, time))

    def speed_instant(self) -> float:
        if len(self.wind_events) == 0:
            return 0
        
        return self.wind_events[-1].speed_km

    def _speed_avg(self, age_seconds: int):
        if len(self.wind_events) == 0:
            return 0

        numerator = 0
        denominator = 0

        for event in self.wind_events:
            time_since = datetime.now() - event.start_time

            if time_since.seconds > age_seconds:
                continue

            numerator += event.speed_km
            denominator += 1

        return numerator / denominator

    def speed_avg_2m(self):
        return self._speed_avg(2 * 60)

        


class RainEvent:
    def __init__(self, amount_mm: float, time: datetime):
        self.amount_mm = amount_mm
        self.time = time
    
    def toJSON(self):
        return json.dumps({ 'amount_mm': self.amount_mm, 'time': self.time })

class RainTracker(PersistentStore):
    rain_events: List[RainEvent] = []

    def __init__(self):
        super().__init__('rain_tracker', 'rain_events')

    def _clean_up(self):
        max_age_hours = 24
        max_age_minutes = max_age_hours * 60
        max_age_seconds = max_age_minutes * 60

        self.rain_events = list(filter(lambda event: (datetime.now() - event.time).seconds < max_age_seconds, self.rain_events))
        self._store()

    def register_rain(self, rain: RainEvent):
        self._clean_up()

        self.rain_events.append(rain)
        return self

    def _get_total(self, age_seconds: int) -> float:
        rain = 0
        now = datetime.now()

        for event in self.rain_events:
            time_since = now - event.time

            if time_since.seconds > age_seconds:
                continue

            rain += event.amount_mm

        return rain

    def get_past_hour(self) -> float:
        """
        Returns the number of mm of rain in the past hour
        """
        return self._get_total(60 * 60)
    
    def get_past_day(self) -> float:
        return self._get_total(60 * 60 * 24)

        
