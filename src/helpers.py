from datetime import datetime
from typing import List

class WindEvent:
    def __init__(self, speed_km: float, start_time: datetime):
        self.speed_km = speed_km
        self.start_time = start_time

class WindTracker:
    wind_events: List[WindEvent]
    speed_per_second: float
    """The wind speed at one pulse / second"""

    def clean_up(self):
        max_age_minutes = 10
        max_age_seconds = max_age_minutes * 60

        self.wind_events = filter(lambda event: (datetime.now() - event.start_time).seconds < max_age_seconds, self.wind_events)

    def add_event(self, time: datetime):
        self.clean_up()

        last_time = self.wind_events[-1].start_time
        dif = time - last_time
        speed = (1/dif.seconds()) * self.speed_per_second

        self.wind_events.append(WindEvent(speed, time))

    def speed_instant(self):
        return self.wind_events[-1].speed_km

    def _speed_avg(self, age_seconds: int):
        numerator = 0
        denominator = 0

        for event in self.wind_events:
            time_since = datetime.now() - event.start_time

            if time_since > age_seconds:
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

class RainTracker:
    rain_events: List[RainEvent] = []

    def register_rain(self, rain: RainEvent):
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

        
