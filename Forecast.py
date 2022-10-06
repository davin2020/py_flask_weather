class Forecast:
    def __init__(self, time, weather_type, temp, rain):
        self.time = time
        self.weather_type = weather_type
        self.temp = temp
        self.rain = rain

    # how to return formatted stuff?
    def __str__(self):
        return f"Forecast: time {self.time}, weather_type {self.weather_type}, temp {self.temp}, rain {self.rain} "

    def printme(self):
        print(f" time {self.time}, weather_type {self.weather_type}, temp {self.temp}, rain {self.rain} ")
