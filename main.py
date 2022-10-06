from datetime import datetime, timedelta
import requests
import json
import urllib

from api_key import API_KEY
from flask import Flask, render_template
from operator import itemgetter
from collections import OrderedDict

# import Location
from Location import Location
from Forecast import Forecast

app = Flask(__name__)

KEY_NOT_FOUND = 0
ALL_SITES_URL =  "http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/sitelist?key=c4fe2801-ff1b-4cd7-8928-ce3aa6a8ae32"
SITELIST_URL = "http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/sitelist?key="

dict_locations = {} #dictionary of locations and ids
location_list = []

# new class stuff
# location_forecast_list = [] #this should NOT be global

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

def setup_locations_forecasts():
    print("setup_locations_forecasts")

@app.route('/locations')
def locations():
    parsedJson = get_url_data(SITELIST_URL)
    all_locations = parsedJson["Locations"]["Location"]

    # create new dict of locations and ids, then sort it by name so it can be printed in alphabetical order for user
    for locn in all_locations:
        location_name = locn["name"]
        location_id = locn["id"]
        dict_locations[location_name] = location_id

        # new stuff w classes
        new_locn = Location(location_id, location_name, {})
        location_list.append(new_locn)
        # current_entry = transaction.Transaction(date, from_person, to_person, details, pence_amount)
        # csv_transactions.append(current_entry)

    # print(f"_location_list ")
    # for i in location_list:
    #     # print(i.name)
    #     print(i.printme())

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

    # new stuff to process data into objs - print first
    # process_data(result)



    # print("weather type 15")
    # print(WEATHER_TYPES[23])

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
    print(f"_ print datetime_str {datetime_str} ")

    # new stuff w classes
    # def __init__(self, time, weather_type, temp, rain):

    # this is useful and working
    # new_forecast = Forecast(starting_minutes, 7, 20,  10)
    # new_forecast2 = Forecast(starting_minutes, 9, 22, 11)
    # location_forecast_list.append(new_forecast)
    # location_forecast_list.append(new_forecast2)

    # assign stuff to dict using = not : symbol ! BUT its still empty and totally not working
    # dict_location_forecast[datetime_str] = location_forecast_list

    # Adding a list directly to a dictionary
    # You can convert a list into a value for a key in a python dictionary using dict() function
        # Values = [18, 20, 25, 29, 30]
        # Details = dict({"Age": Values})
        # print(Details)

    # location_list.append(new_locn)
    # dict_locations[location_name] = location_id

    # correct syntax  to add list of stuff to dict - but location_forecast_list shoudl nto be global!?
    # dict_location_forecast = {datetime_str: location_forecast_list}

    # dict_location_forecast = dict({datetime_str : location_forecast_list})

    # this is useful and working
    # print_dict_list_2(dict_location_forecast)
    # print_locations_dict(dict_location_forecast)


    # new stuff to process data into objs - print first
    # now add location and forecast together and pass whole obj to next page?
    result_dict_location_forecast = process_data(result)

    # new_forecast = Forecast(start_time, weather_type, temperature, rain_probability)
    # result_dict_location_forecast
    # current_location = Location(id locn_name, result_dict_location_forecast)
    current_location = Location(id, locn_name, result_dict_location_forecast)
    # current_location3 = Location(123, "town", [])


    # now pass current lcoation and ALL THE STUFF to the next page?
    print("__current_location")
    str_rtn = current_location.print_me()
    print(str_rtn)

    # weather=result, means name of variable `weather` plus its value `results` is passed to next page
    # return render_template("weather.html", weather_time_period=result, name=locn_name, starting_date=start_time_obj, weather_types=WEATHER_TYPES, visibility_types=VISIBILITY_TYPES)

    # RETURN NEW OBJ
    return render_template("forecast.html", current_location_forecast=current_location, weather_types=WEATHER_TYPES, visibility_types=VISIBILITY_TYPES, starting_date=start_time_obj, current_date=start_time_obj)


def process_data(time_period)->dict:
    print("process_data")
    # new_forecast = Forecast(start_time, weather_type, temperature, rain_probability)
    # current_location = Location(123, "town", [])

    for p in time_period:
        date = p["value"]
        print(f"\nDate: {date}")

        # restart w empty list of forecasts! and shouldnt be global else forecasts for othe dates will get added to it!
        location_forecast_list = []

        # add new date to dict as key, with empty list of forecast objs as value
        tmp_datetime_str = date.rstrip("Z") + " 00:00:00"
        dict_location_forecast[tmp_datetime_str] = []

        from_hour = 0000
        print(f"  Time        Weather Type:  Wind Gust:  Wind Speed:  Wind Dir:  Temp:  Feels Like:  Rel Humidity:  Vis:  Max UV:  Rain: ")

        # loop over the available time periods under 'Rep' - may be less than 8 for todays date
        for i in range(len(p["Rep"])):
            wind_direction = p["Rep"][i]["D"]
            feels_like = p["Rep"][i]["F"]
            wind_gust = p["Rep"][i]["G"]
            relative_humidity = p["Rep"][i]["H"]
            temperature = p["Rep"][i]["T"]
            visibility = p["Rep"][i]["V"]
            wind_speed = p["Rep"][i]["S"]
            max_uv = p["Rep"][i]["U"]
            # todo substitute in words instead of ids, using separate dict for weather type
            weather_type = p["Rep"][i]["W"]
            rain_probability = p["Rep"][i]["Pp"]

            # updated dates - could try modulo for hrs, could parse in zulu time date?
            hour_period_int = int(p["Rep"][i]["$"])  #eg 540 mins after midnight is 9pm
            # datetime_str = ' "2022-10-04Z"
            datetime_str = date.rstrip("Z") + " 00:00:00"
            datetime_object = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')

            # improved date formatting using  $ value from json and turning into DateTime obj
            start_time = datetime_object + timedelta(minutes=hour_period_int)
            final_time = start_time + timedelta(minutes=180)

            # tmp_start_time = datetime_object + hour_period_int
            print(f"start_time: {start_time}")
            # print(f"tmp_start_time: {tmp_start_time}")

            # ? better logic for time?
            # ?? start_time_obj = datetime_object + timedelta(minutes=starting_minutes)
            # {% set amt = i["$"]|int %}
            #             {% set amt_hr = (amt / 60)|int %}
            #     <!--    NOW WORKING OK                    amt_hr {{ amt_hr }}-->
            #
            #             {% set t3 = starting_date.replace(hour=amt_hr) %}

            tmp_amt_hr = int(hour_period_int / 60)
            tmp_time = start_time.replace(hour=tmp_amt_hr)
            print(f"tmp_amt_hr: {tmp_amt_hr}")
            print(f"tmp_time: {tmp_time}")


            # now turn the data into objs and add to list of location, then dict of forecasts
            # (self, time, weather_type, temp, rain):
            # wromg stuff is being added here, from prev day
            new_forecast = Forecast(start_time, weather_type, temperature,  rain_probability)
            # new_forecast2 = Forecast(starting_minutes, 9, 22, 11)
            location_forecast_list.append(new_forecast)
            # location_forecast_list.append(new_forecast2)

            # correct syntax  to add list of stuff to dict
            # dict_location_forecast = {datetime_str: location_forecast_list}

            # from dex
            # dict_location_forecast = {datetime_str: location_forecast_list}
            # dict_location_forecast = {}
            # dict_location_forecast[datetime_str] = location_forecast_list

            # dont add thsi here inside the forecast loop
            # dict_location_forecast[datetime_str] = location_forecast_list

            # this is useful and working
            # print_dict_list_2(dict_location_forecast)
            # print_locations_dict(dict_location_forecast)

            #   final formatting w better dates - this is causing BUG - TypeError: unsupported format string passed to list_iterator.__format__ //  but no need to print any more
            # print(f"{start_time.strftime('%H')}{start_time.strftime('%M')} - {final_time.strftime('%H')}{final_time.strftime('%M')} :  {weather_type:->11}  {wind_gust:->10}  {wind_speed:.>11}  {wind_direction:.>10}  {temperature:->5}  {feels_like:->11}  {relative_humidity:.>13} {visibility:.>4}  {max_uv:->7}  {rain_probability:->5}")
        # above keeps building the forecast list, isntead of adding it to the dict !
        # outside of FOR loop for items in time period

        # Updating existing key's value
        # word_freq.update({'Hello': 99})

        # BUG has sthis stopped  working?
        # dict_location_forecast.update({tmp_datetime_str : location_forecast_list})
        dict_location_forecast[tmp_datetime_str] = location_forecast_list #was working

        # only print dict after it has been updated!
        print_locations_dict(dict_location_forecast)

    #    return the processed data ie location obj with forecasts inside, to calling func, to pass to webpage  - this return needs to be at top/outer level of func in order to work!!
    return dict_location_forecast


# this works to print nested dict that has list in it ok
def print_locations_dict(dict_with_list):
    print("\nprint_locations_dict")
    for key in dict_with_list:
        # print(key.printme(), ': ', all_locn_dict[key].printme())
        print(f"\nkey DATE {key}")
        forecast_list = dict_with_list[key]
        for item in forecast_list:
            # print("_string rep of obj")
            print(str(item))

def print_dict_list_2(dict_list):
    # this is another way to print list inside of dict
    print("\n_ print forecast 245 ")
    for key, values in dict_location_forecast.items():
        print(key)
        for i in values:
            # print(key, " : ", i.printme())
            print(key, " : ", str(i))

    # for key, values in dict_location_forecast.items():
    #     for i in values:
    #         print(key, " : ", i)

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