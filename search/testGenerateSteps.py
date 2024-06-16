from math import cos, radians

import numpy as np
from geopy.distance import geodesic
from pointFullInfo import PointFullInfo
from helpers.nodeInfo import NodeInfo


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


def calculate_time_by_lat_lon(lat1, lon1, lat2, lon2, mapMask, info, caravan, speed):
    x1, y1 = mapMask.decoder(lat1, lon1)
    x2, y2 = mapMask.decoder(lat2, lon2)
    points = bresenham_line((x1, y1), (x2, y2))
    kilometers = geodesic((lat1, lon1), (lat2, lon2)).kilometers
    km = kilometers / len(points)
    speed_kmh = speed * 1.852
    time = 0
    for x, y in points:
        if not mapMask.is_aqua(x, y):
            return -1
        index = mapMask.get_ice_index(x, y)
        if index == 0:
            _, _, index = find_nearest_index(mapMask, x, y)

            if index==0: 
                print('index')
                time += kilometers / speed_kmh * index
        elif index == 1000 or info[f'{index}'][caravan]==-1:
            return -1
        elif index == 3 or index == 2 or index == 1:
            
            time += kilometers / (info[f'{index}'][caravan]*speed * 1.852) * 3600
        else:
            time += kilometers / speed_kmh * index


    return time


def find_nearest_index(map_mask, start_x, start_y, step_size=2, max_steps=10):
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1),  # по осям x и y
                  (1, 1), (-1, 1), (1, -1), (-1, -1)]  # по диагонали

    for i in range(1, max_steps + 1):
        for dx, dy in directions:
            new_x = start_x + dx * step_size * i
            new_y = start_y + dy * step_size * i

            # Обработка выхода за границы по оси Y
            if new_y < 0 or new_y >= map_mask.map_height:
                continue
            
            # Обработка выхода за границы по оси X
            if new_x < 0:
                new_x = map_mask.map_width + new_x
            elif new_x >= map_mask.map_width:
                new_x = new_x - map_mask.map_width

            index = map_mask.get_ice_index(new_x, new_y)
            if index != 0:
                return new_x, new_y, index
    return start_x, start_y, map_mask.get_ice_index(start_x, start_y)

def calculate_time(start_point, end_point, map_mask, info, caravan, speed):
    kilometers = geodesic((start_point.lat, start_point.lon), (end_point.lat, end_point.lon)).kilometers
    index = map_mask.get_ice_index(end_point.x, end_point.y)
    speed_kmh = speed * 1.852
    time = 0
    if index == 0:
        _, _, index = find_nearest_index(map_mask, end_point.x, end_point.y)

        if index==0: 
            print('index')
            time += kilometers / speed_kmh * index
    elif index == 1000 or info[f'{index}'][caravan]==-1:
        return -1
    elif index == 3 or index == 2 or index == 1:
        
        time += kilometers / (info[f'{index}'][caravan]*speed * 1.852) * 3600
    else:
        time += kilometers / speed_kmh * index
    end_point.current_time += time
#    end_point.map_mask.change_ice_map(end_point.current_time)
    return time
def get_ice_index(lat, lon, previous_index, mapMask):
    x1, y1 = mapMask.decoder(lat, lon)
    index = mapMask.get_ice_index(x1, y1)
    if index != 0:
        return index
    return previous_index


def f_cost(g_cost, h_cost, weight=0.5):
    return weight * g_cost + (1 - weight) * h_cost


def optimize(path, map_mask, info, caravan, speed):
    i = 1
    while i < len(path) - 1:
        current_point = path[i]

        next_point = path[i + 1]

        prev_point = path[i - 1]

        current_time = current_point.time_in_path + next_point.time_in_path + prev_point.time_in_path

        direct_time = calculate_time_by_lat_lon(prev_point.lat, prev_point.lon, next_point.lat, next_point.lon,
                                                map_mask, info, caravan, speed)

        if direct_time < current_time and direct_time != -1:
            next_point.set_time(direct_time)
            path.pop(i)

        else:
            i += 1

def generate_points(point, map_mask, visited, info, caravan, speed):
    points = []
    distance = 1
    offsets = [-distance, 0, distance]
    for dx in offsets:
        for dy in offsets:
            if dx == 0 and dy == 0:  # Skip the original point
                continue
            # if abs(dx) == distance or abs(dy) == distance:
            x, y = point.x + dx, point.y + dy
            if map_mask.is_aqua(x, y):
                new_point = NodeInfo.from_xy(x, y, 0, point.map_mask, point.current_time)
                time = calculate_time(point, new_point, map_mask, info, caravan, speed)
                if time != -1:
                    new_point.set_time(time)
                    if (x, y) not in visited or new_point.time_in_path < visited[(x, y)].time_in_path:
                        points.append(new_point)
    return points


def check_start_end(map_mask, point, step_size=5, max_steps=70):
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1),  # по осям x и y
                  (1, 1), (-1, 1), (1, -1), (-1, -1)]  # по диагонали
    start_x, start_y =  point.x, point.y
    index = map_mask.get_ice_index(start_x, start_y)
    if index==1000 or index==0:
        print(f'точка недоступна координаты {point.lat,point.lon}')
        for i in range(1, max_steps + 1):
            for dx, dy in directions:
                new_x = start_x + dx * step_size * i
                new_y = start_y + dy * step_size * i

                # Обработка выхода за границы по оси Y
                if new_y < 0 or new_y >= map_mask.map_height:
                    directions.remove((dx,dy))
                    continue
                
                # Обработка выхода за границы по оси X
                if new_x < 0:
                    new_x = map_mask.map_width + new_x
                elif new_x >= map_mask.map_width:
                    new_x = new_x - map_mask.map_width
                aqua = map_mask.is_aqua(new_x, new_y)
                if not aqua: 
                    directions.remove((dx, dy))
                    continue
                index = map_mask.get_ice_index(new_x, new_y)
                if index != 0 and index != 1000 and aqua:
                    point.lat,point.lon = map_mask.reverse_decoder(new_x,new_y)
                    point.x,point.y = new_x,new_y
                    print(f'точка найдена {point.lat,point.lon}')
                    #map_mask.plot_point(point.lat,point.lon)
                    return point
    return point