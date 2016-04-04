#!/usr/bin/python3
# -*- coding: utf-8 -*-
#file: weather.py

#windows , linux
#pip install --user package_name
#python3 -m pip install requests
#python3 -m pip install BeautifulSoup4

#freebsd (NCTU) using python3.4
#python3.4 -m  ensurepip --user
#python3.4 -m pip install --user beautifulsoup4
#python3.4 -m pip install --user requests



import argparse
import requests
import re
from bs4 import BeautifulSoup
import datetime
import os.path
import platform




def get_weather_data( searchname , unit ):
    temp_unit = "F"
    if unit == "c" or unit == "C":
        temp_unit = "C"

    unit = unit.lower()

    woeid_url = "http://woeid.rosselliot.co.nz/lookup/"+searchname
    r = requests.get(woeid_url)
    #print (r.text)
    soup_woeid = BeautifulSoup(r.text,"html.parser")

    woeid_list = soup_woeid.find_all("tr" , "woeid_row")
    if not woeid_list:
        print("Can not find woeid of "+searchname+" !")
        return None
    woeid = woeid_list[0]['data-woeid'] #index0: best correct woeid
    cityname = woeid_list[0]['data-city']



#print( cityname )
    weather_url = "https://weather.yahooapis.com/forecastrss?w={0}&u={1}".format( woeid ,unit)
#print(weather_url)
    weather_html = requests.get(weather_url).text
#print(weather_html)


    soup_weather = BeautifulSoup( weather_html  , "html.parser")


    #handle forecast
    forecast=[]
    for tag in soup_weather.find_all("yweather:forecast" ):
        tmp_str=""
        #convert abbrivate month to full month
        date_abbr =  datetime.datetime.strptime(tag['date'] , "%d %b %Y").date()
        if platform.system() == "Linux" or platform.system() == "FreeBSD" :
            date_full= date_abbr.strftime("%-d %B %Y") #hyphen for removimg leading zero
        else:
            date_full= date_abbr.strftime("%d %B %Y")
        date_full += " "+tag['day']

        tmp_str = date_full+" "+tag['low']+"~"+tag['high']+temp_unit+" "+tag['text']

        forecast.append( tmp_str )

    #handle sunrise/sunset
    suntime = soup_weather.find("yweather:astronomy")
    sunrise = datetime.datetime.strptime( suntime['sunrise'] ,"%I:%M %p" ).time()
    sunset = datetime.datetime.strptime( suntime['sunset'] , "%I:%M %p").time()


    #handle current weather
    current = soup_weather.find("yweather:condition")

    city_info={}
    city_info['name'] = cityname

    city_info['current'] = cityname+", "+current['text']+", "+current['temp']+temp_unit
    city_info['forecast'] = forecast
    #add padding zero on hour
    city_info['suntime'] = "sunrise: "+sunrise.strftime('%I:%M %p').lower()+", "+"sunset: "+sunset.strftime('%I:%M %p').lower()


    return city_info

#print(city_info['suntime'])

#print ( soup.find_all("td" , "woeid") )
#for tag in soup.find_all("td","woeid"):
#        if tag.has_attr('class'):
#            print (tag)





if  __name__ == '__main__':

    locations=[]
    temp_unit = None
    #argument setting

    parser = argparse.ArgumentParser("Weather Indicator")
    group = parser.add_mutually_exclusive_group()

    parser.add_argument("-l", type=str , help="location"  , dest="location" , metavar='locations')
    parser.add_argument("-u", type=str , help="temperature unit", choices=['c','f'] , dest= "unit" ,metavar="unit" )


    group.add_argument("-a", help="equal to -c -d 5", action="store_true" , dest="all" )


    group.add_argument("-c", help="current condition" , action="store_true" , dest="current")
    group.add_argument("-d" ,help="forecast", metavar="day" , dest="forecast")
    parser.add_argument("-s", help="sunset/sunrise" , action="store_true", dest="sun" )

    args = parser.parse_args()


    #check config file & set location
    if os.path.isfile("config.py"):
#print("config.py exists! ")
        temp_unit="F"
        with open( "config.py" , "r") as filein:
            for line in filein:
                text = line.lstrip()
                if text[0] == "#": #ignore comment
                    continue
                else:
                    textlist = text.split("=" , 1 )
                    if textlist[0] == "LOCATION" or  textlist[0] == "location":
                        textlist[1] = textlist[1].replace("\"" , "")
                        locations = [ x.strip() for x in textlist[1].split(',')]
#print(locations)
                    elif textlist[0] == "UNIT" or textlist[0] == "unit":
                        temp_unit = textlist[1].strip()
                        temp_unit = temp_unit.replace("\"" , "")
                        if temp_unit not in  ['c' ,'C' ,'f' ,'F']:
                            print("temperature unit setting fail")
                            print("unit:['C'|'F'|'c'|'f']")
                            print("use default temperature unit")
                        else:
                            temp_unit = temp_unit.upper()
#print("Setting"+temp_unit)
                    else:
                        print("config.py file format wrong")
                        print("Example:")
                        print("LOCATION: hsinchu")
                        print("UNIT: C")


#print("Setting"+temp_unit)
#    print(args.location is None)
#print( locations )
    if( ( args.location is None) and ( not  locations )  ):
        print("Must specify location")
        parser.print_help()
        exit()

    if( ( args.unit is None ) and ( temp_unit is None ) ) :
        print("Must specify type of information --no unit") #no unit
        parser.print_help()
        exit()


    if args.all and args.forecast:
        print("argument conflict error !")
        print("[-a] and [-d day] cannot be used at the same time")
        exit()




#print(args)
    if (args.all or args.current or  args.forecast or args.sun ) == False:
        print("Must specify type of information --no [ -a | -c | -d ][ -s ]")
        parser.print_help()
        exit()

    if args.forecast:
        day = int(args.forecast)
        if day < 1 or day >5:
            print("[-d day] day must be in range 1~5")
            exit()

    if not (args.location is None):
        locations = [ x.strip() for x in args.location.split(',') ]

    if not (args.unit is None) :
        temp_unit=args.unit


    for city in locations:
        if not city: #empty city name
            continue

        info = get_weather_data( city , temp_unit )
        if not info: #return none --> cannot find woeid
            continue
        print( info['name'] )

        if args.all:
            print( info['current'] )
            for text in info['forecast']:
                print( text )
        elif args.current:
            print( info['current'] )

        if args.forecast:
            for i in range( 0 , int(args.forecast) ):
                print(info['forecast'][i])

        if args.sun:
            print( info['suntime'])




    #print("LOCATION:"+str(locations) )
    #print("UNIT:"+temp_unit)
