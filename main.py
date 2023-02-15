"""
This module helps the user to find locations on the map
where films were shot in the year entered by the user.
"""
import re
from math import radians, cos, sin, asin, sqrt
import argparse
import os
import webbrowser
import folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderUnavailable, GeocoderServiceError


parser = argparse.ArgumentParser(description='Create an HTML-page with dots on map')
parser.add_argument('year', type=int)
parser.add_argument('lattitude', type=float)
parser.add_argument('longtitude', type=float)
parser.add_argument('path_to_file', type=str)
arg = parser.parse_args()


def haversine_distance(lattitude1: float, longtitude1: float, lattitude2: float,\
    longtitude2: float) -> float:
    """
    Function, that calculates the haverse distance betweem two dotts in a map
    using their lattitude and longtitude

    :param lattitude1: first point lattitude
    :type lattitude1: float
    :param longtitude1: first point longtitude
    :type longtitude1: float
    :param lattitude2: second point lattitude
    :type lattitude2: float
    :param longtitude2: second point longtitude
    :type longtitude2: float
    :return: haversine distance beetwen two points on a map
    :type return: float
    """
    radius_of_earth = 6367.4445
    d_lattitude = radians(lattitude2 - lattitude1)
    d_longtitude = radians(longtitude2 - longtitude1)
    return radius_of_earth * 2 * asin(sqrt(sin(d_lattitude / 2) ** 2 + cos(radians(lattitude1))\
    * cos(radians(lattitude2)) * sin(d_longtitude / 2) ** 2))


def check_films(year: int, path: str):
    """
    Function, that creates ah HTML-file with given dotts where films were shot

    :param year: year, by which films should be filtered
    :type year: int
    :return: point's lattitude and longtitude (where films was shot)
    :type return: generator object
    """
    with open(path, mode='r', encoding='latin1', errors='ignore') as file:
        films = list(' '.join(line.split()) for line in file.readlines() if f"({year})" in line)
    for film in films:
        res = re.search(r"[A-Za-z]", film[film.index(')'):])
        if 'TV)' in film[film.index(')'):][res.start():]:
            address = film[film.index('TV)') + 4:]
        elif 'V)' in film[film.index(')'):][res.start():]:
            address = film[film.index('V)') + 3:]
        else:
            address = film[film.index(')'):][res.start():]
        geolocator = Nominatim(user_agent="application")
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
        try:
            location = geolocator.geocode(address)
        except GeocoderUnavailable:
            continue
        except GeocoderServiceError:
            continue
        if location:
            yield (location.latitude, location.longitude)


def create_html_map(year: int, user_lattitude: float, user_longtitude: float, path: str) -> None:
    """
    Function, that makes points of map with certain coordinates near user's coordinates.

    :param year: year, by which films should be filtered
    :type year: int
    :param user_lattitude: user's lattitude
    :type user_lattitude: float
    :param user_longtitude: user's longtitude
    :type user_longtitude: float
    :param path: path to file, in which search has to be done
    :type path: str
    :return: None
    """
    films_and_locations = [(user_lattitude, user_longtitude)]
    for film in check_films(year, path):
        films_and_locations.append(film)
    sorted_coordinates = sorted(films_and_locations, key=lambda x:\
    haversine_distance(user_lattitude, user_longtitude, x[0], x[1]))[:10]
    map_html = folium.Map()
    map_html.add_child(folium.Marker(location=[user_lattitude, user_longtitude],
    popup="Моя точка!", icon=folium.Icon()))
    for lattitude, longtitude in sorted_coordinates[1:]:
        map_html.add_child(folium.Marker(location=[lattitude, longtitude], icon=folium.Icon()))
    map_html.save('Map.html')
    filename = 'file:///'+ os.getcwd()+'/' + 'Map.html'
    webbrowser.open(filename)


if __name__ == '__main__':
    create_html_map(arg.year, arg.lattitude, arg.longtitude, arg.path_to_file)
