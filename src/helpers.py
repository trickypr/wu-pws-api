from datetime import datetime
from typing import List

class RainEvent:
    def __init__(self, amount_mm: float, time: datetime):
        self.amount_mm = amount_mm
        self.time = time

class RainTracker:
    rain_events: List[RainEvent]

    def register_rain(self, rain: RainEvent):
        rain_event.append(rain)
        return self

    def get_past_hour(self) -> float:
        """
        Returns the number of mm of rain in the past hour
        """

        rain = 0
        now = datetime.now()

        for event in self.rain_events:
            time_since = now - event.time

            if time_since.seconds > 60 * 60:
                continue

            rain += event.amount_mm

        return rain
