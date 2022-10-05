from datetime import datetime, timedelta
import requests
import json
import urllib

from api_key import API_KEY
from flask import Flask, render_template
from operator import itemgetter
from collections import OrderedDict

app = Flask(__name__)

KEY_NOT_FOUND = 0
ALL_SITES_URL =  "http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/sitelist?key=c4fe2801-ff1b-4cd7-8928-ce3aa6a8ae32"
SITELIST_URL = "http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/sitelist?key="

dict_locations = {} #dictionary of locations and ids

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

    # try new way of sorting dict
    sorted_dict_locations = OrderedDict(sorted(dict_locations.items()))
    print(type(sorted_dict_locations))

    # try to pass the dict not sorted_list - ok now passing dict of type `collections.OrderedDict`
    # locations=dict_locations, means name of variable `locations` plus its value `dict_locations` is passed to next page
    return render_template("locations.html", locations=sorted_dict_locations)

def get_url_data(url):
    content = requests.get(url + API_KEY)
    parsedJson = json.loads(content.text)
    return parsedJson

def sort_location_dict_by_name():
    newlist = sorted(dict_locations, key=itemgetter(0))
    return newlist

@app.route('/weather/<id>')
def show_weather(id):
    print("show_weather")
    # todo - location name is currently in upper case
    result, locn_name = get_location_weather(id)

    print("weather type 15")
    print(WEATHER_TYPES[23])

    # todo - deal w dates and time periods, then pass date obj to next page
    tp = result[0]['value']
    datetime_str = tp.rstrip("Z") + " 00:00:00"
    datetime_object = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    # print(result)
    # now add in delta
    starting_minutes = int(result[0]['Rep'][0]["$"])
    print(starting_minutes)
    start_time_obj = datetime_object + timedelta(minutes=starting_minutes)

    print(f"datetime_object: {datetime_object}")
    # weather=result, means name of variable `weather` plus its value `results` is passed to next page
    return render_template("weather.html", weather_time_period=result, name=locn_name, starting_date=start_time_obj, weather_types=WEATHER_TYPES, visibility_types=VISIBILITY_TYPES)

def get_location_weather(id):
    # caveat - url encoding/parsing as dont trust user imput of id - https://www.urlencoder.io/python/
    # makes url safer, makes special chars percentage encoded treatesd as single value, doesnt stop bad data - would prevent user from putting in own ? themselves
    quoted_id = urllib.parse.quote(id)
    CITY_URL = "http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/" + quoted_id + "?res=3hourly&key="

    res = get_url_data(CITY_URL)
    location_name = res["SiteRep"]["DV"]["Location"]["name"]
    periods = res["SiteRep"]["DV"]["Location"]["Period"]
    # printing output now happens in html page
    return periods, location_name

if __name__ == '__main__':
    app.run()