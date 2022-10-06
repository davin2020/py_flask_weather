class Location:
    def __init__(self, id, name, forecasts):
        self.id = id
        self.name = name
        self.forecasts = forecasts # dict with key of date and value of forecast obj

    # BUG seems this method cant be called from other places? as it returns NoneType
    # return f"Forecast: time {self.time}, weather_type {self.weather_type}, temp {self.temp}, rain {self.rain}"
    def __str__(self):
        locn_str = f"Location: id {self.id}, name {self.name}, forecasts list: "
        # print(self.id)
        # print(self.name)
        for item in range(len(self.forecasts)): #this is dict, not list!
            print()
            locn_str += str(self.forecasts[item])
            # print(item)
        # print(f"_locn fcast tostring: {locn_str}")
        return locn_str

    def print_me(self):
        print("_location print_me()")
        locn_str = f"Location: id {self.id}, name {self.name}, forecasts list: "
        for key in self.forecasts:
            # print(key.printme(), ': ', all_locn_dict[key].printme())
            print(f"\nkey DATE {key}")
            forecast_list = self.forecasts[key]
            for item in forecast_list:
                print(str(item))
        return locn_str


    def printme(self):
        print(self.id)
        print(self.name)
        for i in range(len(self.forecasts)):
            print(str(self.forecasts[i]))