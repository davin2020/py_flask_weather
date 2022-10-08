from datetime import datetime, timedelta
import requests
import json
import urllib

from api_key import API_KEY
from flask import Flask, render_template
from collections import OrderedDict

from Location import Location
from Forecast import Forecast

app = Flask(__name__)

KEY_NOT_FOUND = 0
ALL_SITES_URL =  "http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/sitelist?key=c4fe2801-ff1b-4cd7-8928-ce3aa6a8ae32"
SITELIST_URL = "http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/sitelist?key="

dict_locations = {} #dictionary of locations and ids
location_list = []

dict_location_forecast = {} # dict of forcasts for a given location

WEATHER_TYPES = {
    0: "Clear Night",
    1: "Sunny Day",
    2: "Partly cloudy (night)",
    3: "Partly cloudy (day)",
    4: "Not used",
    5: "Mist",
    6: "Fog",
    7: "Cloudy",
    8: "Overcast",
    9: "Light rain shower (night)",
    10: "Light rain shower (day)",
    11: "Drizzle",
    12: "Light rain",
    13: "Heavy rain shower (night)",
    14: "Heavy rain shower (day)",
    15: "Heavy rain",
    16: "Sleet shower (night)",
    17: "Sleet shower (day)",
    18: "Sleet",
    19: "Hail shower (night)",
    20: "Hail shower (day)",
    21: "Hail",
    22: "Light snow shower (night)",
    23: "Light snow shower (day)",
    24: "Light snow",
    25: "Heavy snow shower (night)",
    26: "Heavy snow shower (day)",
    27: "Heavy snow",
    28: "Thunder shower (night)",
    29: "Thunder shower (day)",
    30: "Thunder" }

VISIBILITY_TYPES = {
    "UN" : "Unknown",
    "VP" : "Very poor",
    "PO" : "Poor",
    "MO" : "Moderate",
    "GO" : "Good",
    "VG" : "Very good",
    "EX" : "Excellent" }

@app.route('/')
def hello_world():
    return 'Hello Weather World!'

@app.route('/locations')
def locations():
    parsedJson = get_url_data(SITELIST_URL)
    all_locations = parsedJson["Locations"]["Location"]

    # create new dict of locations and ids, then sort it by name so it can be printed in alphabetical order for user
    for locn in all_locations:
        location_name = locn["name"]
        location_id = locn["id"]
        dict_locations[location_name] = location_id

        # create new class in addition to list
        new_locn = Location(location_id, location_name, {})
        location_list.append(new_locn)
        #   todo - pass location_list of Location objs to locatioon.html page and output that instead of original sorted_dict_locations

    # new way of sorting dict usig Collections
    sorted_dict_locations = OrderedDict(sorted(dict_locations.items()))
    print(type(sorted_dict_locations))

    # todo sort location_list before sending to next page!!


    # passing dict (not prev sorted list) which is now of type `collections.OrderedDict`
    # locations=sorted_dict_locations, means name of variable `locations` plus its value `sorted_dict_locations` is passed to next page; to retrieve the value refernce the variable `locations`
    # todo - remove sorted_dict_locations
    return render_template("locations.html", locations=sorted_dict_locations, location_list=location_list)

def get_url_data(url):
    content = requests.get(url + API_KEY)
    parsedJson = json.loads(content.text)
    return parsedJson

@app.route('/weather/<id>')
def show_weather(id): #could rename to get_weather_data ?
    # todo - location name is currently in upper case
    result, locn_name = get_location_weather(id)
    # print(result)

    # # todo - deal w dates and time periods, then just pass date obj to next page instead
    tp = result[0]['value']
    datetime_str = tp.rstrip("Z") + " 00:00:00"
    datetime_object = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    starting_minutes = int(result[0]['Rep'][0]["$"])
    start_time_obj = datetime_object + timedelta(minutes=starting_minutes)
    # print(f"datetime_object: {datetime_object}")
    # print(f"_ print datetime_str {datetime_str} ")

    # process data into objs ie combine location and forecast together, and pass whole obj to next page
    result_dict_location_forecast = process_data(result)
    current_location = Location(id, locn_name, result_dict_location_forecast)

    # return new location obj w nested forecast objs, plus dicts for weather types etc - var `current_location_forecast` and its value `current_location` are passed to next page
    # todo - remove current_date from next page so it can be removed from here too - as each time period should have its own date value and time interval value
    return render_template("forecast.html", current_location_forecast=current_location, weather_types=WEATHER_TYPES, visibility_types=VISIBILITY_TYPES, current_date=start_time_obj)

def process_data(time_period)->dict:
    for p in time_period:
        date = p["value"]
        # restart w empty list of forecasts for current time period
        location_forecast_list = []

        # add new date to dict as key, with empty list of forecast objs as value
        tmp_datetime_str = date.rstrip("Z") + " 00:00:00"
        dict_location_forecast[tmp_datetime_str] = []

        # loop over the available time periods under 'Rep' in json data
        for i in range(len(p["Rep"])):
            # wind_direction = p["Rep"][i]["D"]
            # feels_like = p["Rep"][i]["F"]
            # wind_gust = p["Rep"][i]["G"]
            # relative_humidity = p["Rep"][i]["H"]
            temperature = p["Rep"][i]["T"]
            # visibility = p["Rep"][i]["V"]
            # wind_speed = p["Rep"][i]["S"]
            # max_uv = p["Rep"][i]["U"]
            # todo substitute in words instead of ids, using separate dict for weather type
            weather_type = p["Rep"][i]["W"]
            rain_probability = p["Rep"][i]["Pp"]

            # working out start and end times for time periods - alt option to try modulo for hours, could parse in zulu time date format eg date is  "2022-10-04Z"
            hour_period_int = int(p["Rep"][i]["$"])  #eg 540 mins after midnight is 9pm
            datetime_str = date.rstrip("Z") + " 00:00:00"
            datetime_object = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')

            # improved date formatting using $ value from json and turning into DateTime obj
            start_time = datetime_object + timedelta(minutes=hour_period_int)

            # now turn the data into objs and add to list of location, then dict of forecasts
            new_forecast = Forecast(start_time, weather_type, temperature,  rain_probability)
            location_forecast_list.append(new_forecast)

        # outside of FOR loop for items in time period - now add forcasts to dict
        dict_location_forecast[tmp_datetime_str] = location_forecast_list

        # alt correct syntax  to add list of objs to dict
        # dict_location_forecast = {datetime_str: location_forecast_list}

    # return the processed data ie location obj with forecasts inside, to calling func, to pass to webpage - rtn stmt needs to be at top/outer level of func in order to work
    return dict_location_forecast


# this works to print nested dict that has list in it
def print_locations_dict(dict_with_list):
    print("\nprint_locations_dict")
    for key in dict_with_list:
        print(f"\nkey DATE {key}")
        forecast_list = dict_with_list[key]
        for item in forecast_list:
            print(str(item))

# return data to print on webpage
def get_location_weather(id):
    # used url encoding/parsing as best not to trust user input of id - makes url safer, makes special chars % encoded & treated as single values, would stop user from putting in their own ? for query params, tho doesnt stop bad data
    # https://www.urlencoder.io/python/
    quoted_id = urllib.parse.quote(id)
    CITY_URL = "http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/" + quoted_id + "?res=3hourly&key="

    res = get_url_data(CITY_URL)
    location_name = res["SiteRep"]["DV"]["Location"]["name"]
    periods = res["SiteRep"]["DV"]["Location"]["Period"]
    return periods, location_name

if __name__ == '__main__':
    app.run()