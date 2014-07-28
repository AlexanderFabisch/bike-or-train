# Ressources:
# * https://github.com/marcusschiesser/openbahn-api/blob/master/openbahn-api/src/de/marcusschiesser/dbpendler/server/bahnwrapper/ConnectionParser.java
# * https://github.com/yncyrydybyl/ride2go/blob/master/src/connectors/bahn.de.coffee

# Dependencies:
# * requests
# * beautifulsoup
# * tornado
# * jinja

import sys
import requests
import datetime
from BeautifulSoup import BeautifulSoup
from flask import Flask
from jinja2 import Template
import yaml
reload(sys)
sys.setdefaultencoding('utf-8')


def get_connection(start, destination, verbose=0):
    dt = datetime.datetime.now()
    date = "%d.%d.%d" % (dt.day, dt.month, dt.year)
    time = "%d:%d" % (dt.hour, dt.minute)
    query = ("http://mobile.bahn.de/bin/mobil/query.exe/dox?"
             "n=1&"
             "rt=1&"
             "use_realtime_filter=1&"
             "REQ0HafasOptimize1=0%3A1&REQ0HafasSearchForw=1&"
             "REQ0JourneyDate=" + date + "&"
             "REQ0JourneyStopsS0A=1&"
             "REQ0JourneyStopsS0G=" + start + "&"
             "REQ0JourneyStopsS0ID=&"
             "REQ0JourneyStopsZ0A=1&"
             "REQ0JourneyStopsZ0G=" + destination + "&"
             "REQ0JourneyStopsZ0ID=&"
             "REQ0JourneyTime=" + time + "&"
             "REQ0Tariff_Class=2&"
             "REQ0Tariff_TravellerAge.1=35&"
             "REQ0Tariff_TravellerReductionClass.1=0&"
             "REQ0Tariff_TravellerType.1=E&"
             "existOptimizePrice=1&"
             "existProductNahverkehr=yes&"
             "immediateAvail=ON&"
             "start=Suchen")
    if verbose > 1:
        print(query)
    r = requests.post(query)

    html = r.text
    content = BeautifulSoup(html)
    table = content.body.find("table", attrs={"class": "ovTable clicktable"})
    haupt = content.body.find("div", attrs={"class": "haupt"})

    return str(haupt), str(table)


def get_weather(url):
    today = datetime.datetime.now()
    r = requests.post(url)
    html = r.text
    content = BeautifulSoup(html)
    results = []
    for day in range(4):
        date = today + datetime.timedelta(days=day)
        date_str = "%d%02d%02d" % (date.year, date.month, date.day)
        forecast = content.body.find("div", attrs={"id": "item-" + date_str})
        if forecast is None:
            continue

        result = {}
        result["date"] = "%02d/%02d/%d" % (date.day, date.month, date.year)
        result["temperature"] = forecast.find("div", attrs={"class": "forecast-day-temperature"}).text
        result["text"] = forecast.find("div", attrs={"class": "forecast-day-text"}).text
        columns = forecast.find("div", attrs={"class": "forecast-column-container"})
        result["columns"] = columns
        result["times"] = [time.text for time in
                           columns.findAll("div", attrs={"class": "forecast-column-date"})]
        result["temps"] = [temp.text for temp in
                           columns.findAll("div", attrs={"class": "forecast-text-temperature wt-font-light"})]
        result["conditions"] = [condition.text for condition in
                                columns.findAll("div", attrs={"class": "forecast-column-condition"})]
        result["rains"] = [rain.find("span", attrs={"class": "wt-font-semibold"}).text
                 for rain in columns.findAll("div", attrs={"class": "forecast-column-rain"})]
        result["winds"] = [wind.text for wind in
                           columns.findAll("div", attrs={"class": "forecast-wind-text"})]
        results.append(result)

    return results


if __name__ == '__main__':
    app = Flask(__name__)
    config = yaml.load(open("config.yaml", "r"))

    @app.route("/", methods=["GET"])
    def display():
        template = Template(open("layout.html", "r").read())
        content = template.render(config=config, get_connection=get_connection, get_weather=get_weather)
        return content.decode("utf-8")
    app.run(debug=True)
