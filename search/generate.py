from math import cos, radians

import numpy as np
from geopy.distance import geodesic
from pointFullInfo import PointFullInfo
from search.mapmask import MapMask
from helpers.nodeInfo import NodeInfo
from helpers.visited_tree import VisitedRads


def bresenham_line(point1, point2):
    x1, y1 = point1
    x2, y2 = point2

    pixels = []

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    while True:
        pixels.append((x1, y1))
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy

    return pixels


def calculate_time_by_lat_lon(lat1, lon1, lat2, lon2, ice_map, mapMask, ship):
    x1, y1 = mapMask.decoder(lat1, lon1)
    x2, y2 = mapMask.decoder(lat2, lon2)
    points = bresenham_line((x1, y1), (x2, y2))
    kilometers = geodesic((lat1, lon1), (lat2, lon2)).kilometers
    # km = kilometers / len(points)
    # ship_speed = ship.speed
    # speed_kmh = ship_speed * 1.852
    time = 0
    if len(points) < 15:
        try:
            for x, y in points:
                if not mapMask.is_aqua(x, y):
                    return -1
        except:
            pass
    box, _ = ice_map.find_nearest_square((lat2, lon2))
    index = box.index
    if index == 1000:
        return -1
    if index == 3:
        if ship.info['3'] != -1:
            time += kilometers / (ship.info['3'] * 1.852) * 3600
        else:
            return -1
    elif index == 2:
        if ship.info['2'] != -1:
            time += kilometers / (ship.info['2'] * 1.852) * 3600
        else:
            return -1
    elif index == 1:
        time += kilometers / (ship.info['1'] * 1.852) * 3600
    return time


def calculate_time(start_point, end_point, map_mask):
    kilometers = geodesic((start_point.lat, start_point.lon), (end_point.lat, end_point.lon)).kilometers
    ship_speed = 22
    speed_kmh = ship_speed * 1.852
    index = map_mask.get_ice_index(end_point.x, end_point.y)
    time = 0
    if index == 1000:
        return -1
    if index == 3:
        time = kilometers / (14 * 1.852) * 3600
    elif index == 2:
        time = kilometers / (19 * 1.852) * 3600
    elif index <= 1:
        time = kilometers / speed_kmh * 3600
    end_point.current_time += time
    end_point.map_mask.change_ice_map(end_point.current_time)
    return time


def get_ice_index(lat, lon, previous_index, mapMask):
    x1, y1 = mapMask.decoder(lat, lon)
    index = mapMask.get_ice_index(x1, y1)
    if index != 0:
        return index
    return previous_index


def f_cost(g_cost, h_cost, weight=0.5):
    return weight * g_cost + (1 - weight) * h_cost


def optimize(path, map_mask):
    i = 1
    while i < len(path) - 1:
        current_point = path[i]

        next_point = path[i + 1]

        prev_point = path[i - 1]

        current_time = current_point.time_in_path + next_point.time_in_path + prev_point.time_in_path

        direct_time = calculate_time_by_lat_lon(prev_point.lat, prev_point.lon, next_point.lat, next_point.lon,
                                                map_mask)

        if direct_time < current_time and direct_time != -1:
            next_point.set_time(direct_time)
            path.pop(i)

        else:
            i += 1


def generate_points(point, map_mask, visited: VisitedRads, ice_map, ship, distance_km=5, step_degrees=30):
    points = []

    for angle in range(0, 360, step_degrees):
        destination = geodesic(kilometers=distance_km).destination((point.lat, 0), angle)
        destination.longitude = destination.longitude + point.lon
        if map_mask.is_aqua(destination.latitude, destination.longitude):
            time = calculate_time_by_lat_lon(point.lat, point.lon, destination.latitude, destination.longitude,
                                             ice_map, map_mask, ship)
            if time != -1:
                dd = NodeInfo(destination.latitude, destination.longitude, time, time+point.current_time)

                test = visited.find_nearest_rad((dd.lat, dd.lon), time)
                if not test:
                    if test != False:
                        if test.time > time:
                            test.time = time
                        else:
                            continue
                    visited.add_rads((dd.lat, dd.lon), time)
                    points.append(dd)
                # visited.pop()

            # points.append((destination.latitude, destination.longitude))

    return points
