import requests
from api.src.helpers import RainTracker, WindTracker

from api.src.utils import celsius_to_farenheight, hpa_to_inhg, kph_to_mph, mm_to_inches


class Request:
    """A wrapper around the request that is sent to weather underground. Based
    on the docs provided here:
    https://support.weather.com/s/article/PWS-Upload-Protocol?language=en_US
    """

    params = {}

    def __init__(self, api_object):
        self.api_object = api_object

    def temperature_celsius(self, temperature: float):
        self.params['tempf'] = celsius_to_farenheight(temperature)
        return self

    def humidity(self, humidity: float):
        if humidity > 100 or humidity < 0:
            raise ValueError(f"The humidity must have a value between 0 and 100%, got {humidity}%")

        self.params['humidity'] = humidity
        return self

    def pressure_hpa(self, pressure: float):
        self.params['baromin'] = hpa_to_inhg(pressure)
        return self

    def uv_index(self, uv_index: float):
        self.params['UV'] = uv_index
        return self

    def hourly_rain_mm(self, rain: float):
        self.params['rainin'] = mm_to_inches(rain)
        return self

    def daily_rain_mm(self, rain: float):
        self.params['dailyrainin'] = mm_to_inches(rain)
        return self
    
    def wind_instant_mph(self, speed: float):
        self.params['windspeedmph'] = speed
        return self
    
    def wind_gust_mph(self, speed: float):
        self.params['windgustmph'] = speed
        return self
    
    def wind_speed_mph_2m(self, speed: float):
        self.params['windspdmph_avg2m'] = speed
        return self
    
    def wind_gust_mph_10m(self, speed: float):
        self.params['windgustmph_10m'] = speed
        return self

    def wind_instant_kph(self, speed: float):
        return self.wind_instant_mph(kph_to_mph(speed))
    
    def wind_gust_kph(self, speed: float):
        return self.wind_gust_mph(kph_to_mph(speed))
    
    def wind_speed_kph_2m(self, speed: float):
        return self.wind_speed_mph_2m(kph_to_mph(speed))
    
    def wind_gust_kph_10m(self, speed: float):
        return self.wind_gust_mph_10m(kph_to_mph(speed))

    def wind(self, wind: WindTracker):
        return self.wind_instant_kph(wind.speed_instant()).wind_speed_kph_2m(wind.speed_avg_2m())

    def rain(self, rain: RainTracker):
        return self.hourly_rain_mm(rain.get_past_hour()).daily_rain_mm(rain.get_past_day())

    def calculate_other_vals(self):
        if self.params['tempf'] is not None and self.params['humidity'] is not None:
            self.params['dewptf'] = self.params['tempf'] - ((100 - self.params['humidity']) / 5)

    def send(self) -> requests.Response:
        self.calculate_other_vals()
        
        stringified_params = f"?ID={self.api_object.station_id}&PASSWORD={self.api_object.password}&dateutc=now"

        for param, value in self.params.items():
            stringified_params += f"&{param}={value}"
        
        stringified_params += "&action=updateraw"

        print(f"{self.api_object.api_url}{stringified_params}")
        return requests.get(f"{self.api_object.api_url}{stringified_params}")




        

class API:
    station_id: str 
    password: str

    api_url: str = "https://weatherstation.wunderground.com/weatherstation/updateweatherstation.php"
    api_additional_params = {}

    def __init__(self, station_id: str, password: str):
        self.station_id = station_id
        self.password = password
    
    def change_api_url(self, url: str) -> None:
        """
        Changes the api that personal weather station data will be uplaoded to.
        Do not mess with this unless you know what you are doing. 
        """
        self.api_url = url

    def use_realtime(self, time_between_updates: float):
        """Sends realtime (also known as RapidFire) data to the server

        Args:
            time_between_updates (float): The time (in seconds) between upates.

        Raises:
            ValueError: If the time is less than 2.5
        """

        if time_between_updates < 2.5:
            raise ValueError(f"The time between updates must be more than 2.5 seconds. Got {time_between_updates} seconds")

        self.api_url = "https://rtupdate.wunderground.com/weatherstation/updateweatherstation.php"

        self.api_additional_params["realtime"] = 1
        self.api_additional_params["rtfreq"] = time_between_updates

        return self

    def start_request(self) -> Request:
        req = Request(self)
        req.params = self.api_additional_params
        return req
