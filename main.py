"""
This module helps the user to find locations on the map
where films were shot in the year entered by the user.
"""
import re
from math import radians, cos, sin, asin, sqrt
import argparse
import os
import webbrowser
from typing import Tuple
from functools import lru_cache
import folium
from geopy.geocoders import Nominatim


parser = argparse.ArgumentParser(description='Create an HTML-page with dots on map')
parser.add_argument('year', type=int)
parser.add_argument('latitude', type=float)
parser.add_argument('longtitude', type=float)
parser.add_argument('path_to_file', type=str)
arg = parser.parse_args()


@lru_cache(maxsize=None)
def get_coordinates(address: str) -> Tuple[float, float]:
    """
    Function, that returns a coordinate of location with help of decorator lru_cache.
    :paran address: address of place, giving like a string
    :type address: str
    :return: coordinates(latitude, longtitude)
    :return type: tuple
    """
    try:
        geolocator = Nominatim(user_agent="app")
        location = geolocator.geocode(address)
        return (location.latitude, location.longitude)
    except Exception:
        return None

def haversine_distance(latitude1: float, longtitude1: float, latitude2: float,\
    longtitude2: float) -> float:
    """
    Function, that calculates the haverse distance betweem two dotts in a map
    using their latitude and longtitude

    :param latitude1: first point latitude
    :type latitude1: float
    :param longtitude1: first point longtitude
    :type longtitude1: float
    :param latitude2: second point latitude
    :type latitude2: float
    :param longtitude2: second point longtitude
    :type longtitude2: float
    :return: haversine distance beetwen two points on a map
    :type return: float
    """
    radius_of_earth = 6367.4445
    d_latitude = radians(latitude2 - latitude1)
    d_longtitude = radians(longtitude2 - longtitude1)
    return radius_of_earth * 2 * asin(sqrt(sin(d_latitude / 2) ** 2 + cos(radians(latitude1))\
    * cos(radians(latitude2)) * sin(d_longtitude / 2) ** 2))


def check_films(year: int, path: str):
    """
    Function, that creates ah HTML-file with given dotts where films were shot

    :param year: year, by which films should be filtered
    :type year: int
    :return: point's latitude and longtitude (where films was shot)
    :type return: generator object
    """
    with open(path, mode='r', encoding='latin1', errors='ignore') as file:
        films = list(' '.join(line.split()) for line in file.readlines() if f"({year})" in line)
    for film in films:
        film = re.sub(r'\"[^""]*\"', '', film)
        film = film[film.index(')'):]
        if '}' in film:
            if '(V)' in film or '(TV)' in film:
                film = film[film.index('V'):]
            address = film[film.index('}') + 2:]
        else:
            if '(V)' in film or '(TV)' in film:
                address = film[film.index('V') + 3:]
            else:
                address = film[2:]
        location = get_coordinates(address)
        if location:
            yield location

def create_html_map(year: int, user_latitude: float, user_longtitude: float, path: str) -> None:
    """
    Function, that makes points of map with certain coordinates near user's coordinates.

    :param year: year, by which films should be filtered
    :type year: int
    :param user_latitude: user's latitude
    :type user_latitude: float
    :param user_longtitude: user's longtitude
    :type user_longtitude: float
    :param path: path to file, in which search has to be done
    :type path: str
    :return: None
    """
    points_that_already_on_the_map = set()
    points_that_already_on_the_map.add((user_latitude, user_longtitude))
    map_html = folium.Map(tiles='Stamen Toner', location=\
    [user_latitude, user_longtitude], zoom_start=5)
    map_html.add_child(folium.Marker(location=[user_latitude, user_longtitude],
    popup="Your place!", icon=folium.Icon(color='lightgray', icon='home')))
    for latitude, longtitude  in check_films(year, path):
        if (latitude, longtitude) not in points_that_already_on_the_map\
         and haversine_distance(user_latitude, user_longtitude, latitude, longtitude) < 800:
            child_marker = folium.Marker(location=[latitude, longtitude],\
            icon=folium.Icon(color='red'))
            map_html.add_child(child_marker)
            points_that_already_on_the_map.add((latitude, longtitude))
            if len(points_that_already_on_the_map) == 10:
                break
    map_html.save('Map.html')
    filename = 'file:///' + os.getcwd() + '/' + 'Map.html'
    webbrowser.open(filename)


if __name__ == '__main__':
    create_html_map(arg.year, arg.latitude, arg.longtitude, arg.path_to_file)
