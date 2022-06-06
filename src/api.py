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
        """Creates a request object, which can have data added to it and be sent
        off to weather underground for processing

        Args:
            api_object (API): The parent API object, which contains the critical
            information for logging on
        """

        self.api_object = api_object

    def temperature_celsius(self, temperature: float):
        """Send the temperature in celsius to WU

        Args:
            temperature (float): The temperature in °C

        Returns:
            Request: The request object for chaining
        """

        self.params['tempf'] = celsius_to_farenheight(temperature)
        return self

    def humidity(self, humidity: float):
        """Send the humidity to weather underground

        Args:
            humidity (float): The humidity

        Raises:
            ValueError: When the humidity is above 100% or bellow 0% something
            is going wrong

        Returns:
            Request: Used for chaining data additions
        """

        if humidity > 100 or humidity < 0:
            raise ValueError(
                f"The humidity must have a value between 0 and 100%, got {humidity}%"
            )

        self.params['humidity'] = humidity
        return self

    def pressure_hpa(self, pressure: float):
        """Sends the pressure up to WU

        Args:
            pressure (float): The pressure in hPa

        Returns:
            Request: Used for chaining data additions
        """

        self.params['baromin'] = hpa_to_inhg(pressure)
        return self

    def uv_index(self, uv_index: float):
        """Sends the UV index to WU

        Args:
            uv_index (float): The uv index

        Returns:
            Request: Used for chaining data additions
        """

        self.params['UV'] = uv_index
        return self

    def hourly_rain_mm(self, rain: float):
        """The amount of rain that has fallen in the past hour

        Args:
            rain (float): The amount of rain in mm 

        Returns:
            Request: Used for chaining data additions
        """

        self.params['rainin'] = mm_to_inches(rain)
        return self

    def daily_rain_mm(self, rain: float):
        """Send the amount of daily rain up to weather underground

        Args:
            rain (float): The amount of rain in mm

        Returns:
            Request: Used for chaining data additions
        """

        self.params['dailyrainin'] = mm_to_inches(rain)
        return self

    def wind_instant_mph(self, speed: float):
        """Sens the instantaneous wind sped to weather underground

        Args:
            speed (float): The wind speed in mph

        Returns:
            Request: Used for chaining data additions
        """

        self.params['windspeedmph'] = speed
        return self

    def wind_gust_mph(self, speed: float):
        """Send the gust speed to WU

        Args:
            speed (float): The gust speed in mph

        Returns:
            Request: Used for chaining data additions
        """

        self.params['windgustmph'] = speed
        return self

    def wind_speed_mph_2m(self, speed: float):
        """Sends the average wind speed for the past 2 minutes to WU

        Args:
            speed (float): The average wind speed over the past 2 minutes in mph

        Returns:
            Request: Used for chaining data additions
        """

        self.params['windspdmph_avg2m'] = speed
        return self

    def wind_gust_mph_10m(self, speed: float):
        """Sends the gust speed for the past 10 minutes to WU

        Args:
            speed (float): The gust speed for the past 10 minutes in mph

        Returns:
            Request: Used for chaining data additions
        """

        self.params['windgustmph_10m'] = speed
        return self

    def wind_instant_kph(self, speed: float):
        """The instantaneous wind speed in kph

        Args:
            speed (float): The wind speed in kph

        Returns:
            Request: Used for chaining data additions
        """

        return self.wind_instant_mph(kph_to_mph(speed))

    def wind_gust_kph(self, speed: float):
        """The gust speed in kph

        Args:
            speed (float): The gust speed in kph

        Returns:
            Request: Used for chaining data additions
        """

        return self.wind_gust_mph(kph_to_mph(speed))

    def wind_speed_kph_2m(self, speed: float):
        """Sends the average wind speed for the past 2 minutes to WU

        Args:
            speed (float): The average wind speed over the past 2 minutes in kph

        Returns:
            Request: Used for chaining data additions
        """

        return self.wind_speed_mph_2m(kph_to_mph(speed))

    def wind_gust_kph_10m(self, speed: float):
        """Sends the gust speed for the past 10 minutes to WU

        Args:
            speed (float): The gust speed for the past 10 minutes in kph

        Returns:
            Request: Used for chaining data additions
        """

        return self.wind_gust_mph_10m(kph_to_mph(speed))

    def wind_direction_instant(self, angle: float):
        """Sends the instantaneous wind direction to WU

        Args:
            angle (float): The instantaneous wind direction

        Returns:
            Request: Used for chaining data additions
        """

        self.params['winddir'] = angle
        return self

    def wind_direction_2m(self, angle: float):
        """Sends the average wind direction for the past 2 minutes to WU

        Args:
            angle (float): The average wind direction over the past 2 minutes

        Returns:
            Request: Used for chaining data additions
        """

        self.params['winddir_avg2m'] = angle
        return self

    def wind(self, wind: WindTracker):
        """Sends all of the data from the WindTracker object to WU

        Args:
            wind (WindTracker): The wind tracker object for your weather station

        Returns:
            Request: Used for chaining data additions
        """

        return self.wind_instant_kph(wind.speed_instant()).wind_speed_kph_2m(
            wind.speed_2m()).wind_direction_instant(
                wind.direction_instant()).wind_direction_2m(
                    wind.direction_2m())

    def rain(self, rain: RainTracker):
        """Sends all of the data from the RainTracker object to WU

        Args:
            rain (RainTracker): The rain tracker object for your weather station

        Returns:
            Request: Used for chaining data additions
        """

        return self.hourly_rain_mm(rain.get_past_hour()).daily_rain_mm(
            rain.get_past_day())

    def calculate_other_vals(self):
        """Calculates known values from formulas
        """

        if self.params['tempf'] is not None and self.params[
                'humidity'] is not None:
            self.params['dewptf'] = self.params['tempf'] - (
                (100 - self.params['humidity']) / 5)

    def send(self) -> requests.Response:
        """Sends data up to the weather underground server

        Returns:
            requests.Response: The response from the server
        """

        self.calculate_other_vals()

        stringified_params = f"?ID={self.api_object.station_id}&PASSWORD={self.api_object.password}&dateutc=now"

        for param, value in self.params.items():
            stringified_params += f"&{param}={value}"

        stringified_params += "&action=updateraw"

        print(f"{self.api_object.api_url}{stringified_params}")
        return requests.get(f"{self.api_object.api_url}{stringified_params}")


class API:
    """
    A simple method of storing data about a weather underground PWS and
    creating requests for its api.
    """

    station_id: str
    password: str

    api_url: str = "https://weatherstation.wunderground.com/weatherstation/updateweatherstation.php"
    """
    The API endpoint that the calls will be made to. This can be changed for
    special features or using an alternative service. 
    """
    api_additional_params = {}
    """
    Any additional parameters that should be send to the API. This may include
    special cases, like realtime data
    """
    def __init__(self, station_id: str, password: str):
        """Setup an API object

        Args:
            station_id (str): The ID of this PWS
            password (str): The password of this PWS
        """

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
            raise ValueError(
                f"The time between updates must be more than 2.5 seconds. Got {time_between_updates} seconds"
            )

        self.api_url = "https://rtupdate.wunderground.com/weatherstation/updateweatherstation.php"

        self.api_additional_params["realtime"] = 1
        self.api_additional_params["rtfreq"] = time_between_updates

        return self

    def start_request(self) -> Request:
        """
        Prepares a request object with the nessisary values to send data
        to the weather underground API.
        """
        req = Request(self)
        req.params = self.api_additional_params
        return req
