from datetime import datetime
import statistics
from typing import List, Tuple

import os
import json

store_path = os.getcwd()


class WindEvent:
    def __init__(self, speed_km: float, start_time: datetime, angle: float):
        self.speed_km = speed_km
        self.start_time = start_time
        self.angle = angle

    def toJSON(self):
        return json.dumps({
            'speed_km': self.speed_km,
            'start_time': self.start_time
        })


class WindTracker:
    wind_events: List[WindEvent] = []
    distance_per_event: float = 7 / 6  # meters
    """The distance (in meters) traveled when there is one event"""

    direction_resistance_table: List[Tuple[float, float]]

    def clean_up(self):
        max_age_minutes = 10
        max_age_seconds = max_age_minutes * 60

        self.wind_events = list(
            filter(
                lambda event:
                (datetime.now() - event.start_time).seconds < max_age_seconds,
                self.wind_events))

    def load_direction_table(self, table: List[Tuple[float, float]]):
        self.direction_resistance_table = table
        return self

    def get_direction(self, resistance: float) -> float:
        distances = list(
            map(lambda row: abs(resistance - row[1]),
                self.direction_resistance_table))
        min_index = distances.index(min(distances))
        return self.direction_resistance_table[min_index][0]

    def add_event(self, time: datetime, angle: float):
        self.clean_up()

        if len(self.wind_events) == 0:
            self.wind_events.append(WindEvent(0, time, angle))
            return

        last_time = self.wind_events[-1].start_time
        dif = time - last_time
        dif_seconds = dif.seconds + dif.microseconds / 1000000  # Note that if the time was less than one second, the dif will be zero, so we need to calculate the microseconds
        speed_mps = self.distance_per_event / dif_seconds  # Wind speed in m/s
        speed_kph = speed_mps / 1000 * 60 * 60

        if speed_kph > 1000:
            # THis only happens when there is a double bounce, so we should
            # try to filter it out
            return

        print(f"Wind Speed: {speed_kph}")

        self.wind_events.append(WindEvent(speed_kph, time, angle))

    def speed_instant(self) -> float:
        if len(self.wind_events) == 0:
            return 0

        return self.wind_events[-1].speed_km

    def _avg(self, age_seconds: int, atr: str):
        if len(self.wind_events) == 0:
            return 0

        numerator = 0
        denominator = 0

        for event in self.wind_events:
            time_since = datetime.now() - event.start_time

            if time_since.seconds > age_seconds:
                continue

            numerator += event.__getattribute__(atr)
            denominator += 1

        return numerator / denominator

    def speed_2m(self):
        return self._avg(2 * 60, 'speed_km')

    def direction_instant(self):
        if len(self.wind_events) == 0:
            return 0

        return self.wind_events[-1].angle

    def direction_2m(self):
        return self._avg(2 * 60, 'angle')


class RainEvent:
    def __init__(self, amount_mm: float, time: datetime):
        self.amount_mm = amount_mm
        self.time = time

    def toJSON(self):
        return json.dumps({'amount_mm': self.amount_mm, 'time': self.time})


class RainTracker:
    rain_events: List[RainEvent] = []

    def _clean_up(self):
        max_age_hours = 24
        max_age_minutes = max_age_hours * 60
        max_age_seconds = max_age_minutes * 60

        self.rain_events = list(
            filter(
                lambda event:
                (datetime.now() - event.time).seconds < max_age_seconds,
                self.rain_events))

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
