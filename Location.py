class Location:
    def __init__(self, id, name, forecasts):
        self.id = id
        self.name = name
        self.forecasts = forecasts # dict with key of date and value of forecast obj

    # todo BUG seems this method cant be called from other places? as it returns NoneType
    def __str__(self):
        locn_str = f"Location: id {self.id}, name {self.name}, forecasts list: "
        for item in range(len(self.forecasts)): #this is dict, not list!
            locn_str += str(self.forecasts[item])
        return locn_str

    def print_me(self):
        locn_str = f"Location: id {self.id}, name {self.name}, forecasts list: "
        for key in self.forecasts:
            print(f"\nLocn _print_me key DATE {key}")
            forecast_list = self.forecasts[key]
            for item in forecast_list:
                locn_str += str(item)
                print(str(item))
        return locn_str
