from math import cos, radians

import numpy as np
from geopy.distance import geodesic
from pointFullInfo import PointFullInfo
from search.mapmask import MapMask


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


def add_point(rtree_idx, points_data, point):
    """
    Добавляет точку в R-дерево с фиксированным радиусом 1 км.

    :param rtree_idx: rtree index, созданный из points_data
    :param points_data: список данных о точках
    :param point: объект PointFullInfo
    """
    radius = 10.0  # Радиус в километрах
    lat, lon = point.latitude, point.longitude
    lat_change = radius / 111.0  # 1 градус широты ~ 111 км
    lon_change = radius / (111.0 * abs(cos(radians(lat))))
    rtree_idx.insert(len(points_data), (lon - lon_change, lat - lat_change, lon + lon_change, lat + lat_change))
    # points_data.append(point)


def remove_point(rtree_idx, points_data, index_to_remove):
    point = points_data[index_to_remove]
    radius = 10.0
    lat, lon = point.latitude, point.longitude
    lat_change = radius / 111.0
    lon_change = radius / (111.0 * abs(cos(radians(lat))))
    rtree_idx.delete(index_to_remove, (lon - lon_change, lat - lat_change, lon + lon_change, lat + lat_change))
    points_data.pop(index_to_remove)


def is_point_within_any_radius(point, radius_data, rtree_idx):
    lat, lon = point.latitude, point.longitude

    possible_ids = list(rtree_idx.intersection((lon, lat, lon, lat)))
    for i in possible_ids:
        center, radius = (radius_data[i].latitude, radius_data[i].longitude), 1
        if geodesic(center, (lat, lon)).kilometers <= radius:
            # if point.current_time < radius_data[i].current_time:
            #     remove_point(rtree_idx, radius_data, i)
            #     # radius_data.pop()
            #     return False
            return True
    return False


def calculate_error(latitude1, longitude1, latitude2, longitude2, current_error, mapMask, distance_km):
    x1, y1 = mapMask.decoder(latitude1, longitude1)
    x2, y2 = mapMask.decoder(latitude2, longitude2)

    points = bresenham_line((x1, y1), (x2, y2))

    # x_coords = np.arange(x1, x2 + 1, 1)  # Шаг 1 для целых чисел
    # y_coords = np.arange(y1, y2 + 1, 1)  # Шаг 1 для целых чисел
    # xx, yy = np.meshgrid(x_coords, y_coords)

    # Объединение координат в массив уникальных точек
    # unique_points = np.unique(np.vstack([xx.ravel(), yy.ravel()]).T, axis=0)
    # mapMask.plot_graph_on_map_X_Y(x_coords, y_coords)
    km = distance_km / len(points)
    speed_kmh = 22 * 1.852
    time_seconds = 0
    # mapMask.plot_point_X_Y(points)
    for x, y in points:
        # x = int(round(x))
        # y = int(round(y))
        index = mapMask.get_ice_index(x, y)
        time_hours = None
        if index == 1000:
            return -1
        elif index == 3:
            time_hours = distance_km / (14 * 1.852)
        elif index == 2:
            time_hours = distance_km / (19 * 1.852)
        elif index <= 1:
            time_hours = distance_km / speed_kmh
        time_seconds += time_hours * 3600

    return current_error + time_seconds


def get_ice_index(lat, lon, previous_index, mapMask):
    x1, y1 = mapMask.decoder(lat, lon)
    index = mapMask.get_ice_index(x1, y1)
    if index != 0:
        return index
    return previous_index


def f_cost(g_cost, h_cost, weight=0.5):
    return weight * g_cost + (1 - weight) * h_cost


def generate_points(point, distance_km, step_degrees, mapMask, visited, end_point, tree):
    points = []

    for angle in range(0, 360, step_degrees):
        destination = geodesic(kilometers=distance_km).destination((point.latitude, point.longitude), angle)
        if mapMask.is_aqua(destination.latitude, destination.longitude):
            time = calculate_error(point.latitude, point.longitude, destination.latitude, destination.longitude,
                                   point.current_time, mapMask, distance_km)
            if time != -1:
                ice_index = get_ice_index(destination.latitude, destination.longitude, point.ice_index, mapMask)
                dd = PointFullInfo(destination.latitude, destination.longitude, ice_index, time,
                                   error=geodesic((end_point.latitude, end_point.longitude),
                                                  (destination.latitude, destination.longitude)).kilometers)
                test = is_point_within_any_radius(dd, visited, tree)
                if not test:
                    add_point(tree, visited, destination)
                    visited.append(dd)
                    points.append(dd)
                # visited.pop()

            # points.append((destination.latitude, destination.longitude))

    return points


lat1, lon1 = 69.05482, 73.46008
lat2, lon2 = 41.77131, 153.28125

# some_thing = calculate_error(lat1, lon1, lat2, lon2, 0, MapMask('../resultMap/map_ice_03-Mar-2020.png'), 1000)
# print(some_thing)


# point1 = (2, 3)
# point2 = (10, 8)
# line_pixels = bresenham_line(point1, point2)
# print(line_pixels)