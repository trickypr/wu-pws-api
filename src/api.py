import requests

from api.src.utils import celsius_to_farenheight


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

    def send(self) -> requests.Response:
        stringified_params = f"?ID={self.api_object.station_id}&password={self.api_object.password}&dateutc=now"

        for param, value in self.params.items():
            stringified_params += f"&{param}={value}"
        
        stringified_params += "&action=updateraw"

        print(f"{self.api_object.api_url}{stringified_params}")
        return requests.get(f"{self.api_object.api_url}{stringified_params}")




        

class API:
    station_id: str 
    password: str

    api_url: str = "https://weatherstation.wunderground.com/weatherstation/updateweatherstation.php"

    def __init__(self, station_id: str, password: str):
        self.station_id = station_id
        self.password = password
    
    def change_api_url(self, url: str) -> None:
        """
        Changes the api that personal weather station data will be uplaoded to.
        Do not mess with this unless you know what you are doing. 
        """
        self.api_url = url

    def start_request(self) -> Request:
        return Request(self)
    
