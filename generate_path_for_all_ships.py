# from math import cos, radians
import json
import uuid
from datetime import datetime

import folium
from geopy.distance import geodesic
import networkx as nx
from search.testGenerateSteps import generate_points
from search.testMapMask import MapMask
from ship.getShip import get_ship_by_name
from helpers.nodeInfo import NodeInfo
from helpers.build_tree import Ice
from helpers.visited_tree import VisitedRads


# from pointFullInfo import PointFullInfo
# from rtree import index

def check_start_end(ice_map, point, map_mask):
    cc, _ = ice_map.find_nearest_square((point.lat, point.lon))
    if cc.index == 1000:
        new_point = ice_map.find_clean_water((point.lat, point.lon), map_mask)
        return NodeInfo(new_point.center[0], new_point.center[1], 0., point.current_time)
    return point


def main(start_point, end_point, ship, ice_map):
    G = nx.Graph()
    map_mask = MapMask('resultMap/map_image.png')
    visited = VisitedRads()
    NodeInfo.set_class(end_point[0], end_point[1], map_mask)
    current_time = int(datetime.strptime(ship["startTime"], '%Y-%m-%d %H:%M:%S').timestamp())

    start_point_node = NodeInfo(start_point[0], start_point[1], 0., current_time)
    end_point_node = NodeInfo(end_point[0], end_point[1], 0, current_time)
    start_point_node = check_start_end(ice_map, start_point_node, map_mask)
    end_point_node = check_start_end(ice_map, end_point_node, map_mask)
    NodeInfo.set_class(end_point_node.lat, end_point_node.lon, map_mask)

    G.add_node(start_point_node)
    G.add_node(end_point_node)

    steps = [start_point_node]
    # visited = {}
    i = 0
    is_path_exist = False
    error_status = 0
    while True:
        if len(steps) == 0:
            print("пути нет")
            error_status = 1
            break
        current_point = steps.pop()
        if current_point.distance_to_end <= 10:
            print("Путь есть")
            is_path_exist = True
            G.add_edge(current_point, end_point_node)
            break
        new_steps = generate_points(current_point, map_mask, visited, ice_map, ship)
        for step in new_steps:
            G.add_node(step)
            G.add_edge(current_point, step, weight=step.distance_to_end)
        steps.extend(new_steps)
        steps = sorted(steps, key=lambda x: x.distance_to_end, reverse=True)
        i += 1
        if i >= 1000:
            print("Достигнут предел итераций")
            error_status = 2
            break

    if not is_path_exist:
        # m = folium.Map(location=[25, 25], zoom_start=4)
        #
        # folium.Marker(location=(start_point_node.lat, start_point_node.lon), popup='Start Point').add_to(m)
        # folium.Marker(location=(start_point_node.end_lat, start_point_node.end_lon), popup='End Point').add_to(m)
        shortest_path_array = []
        # if len(visited.rads) != 0:
        if len(visited.rads) != 0:
            for x in visited.rads:
                # edge = visited[(x, y)]
                shortest_path_array.append((x.center[0], x.center[1]))
        try:
            with open('ship/ships_path.json', 'r', encoding='utf8') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = []

        data.append({
            generate_random_id(): {
                "name": ship['name'],
                "start_time": start_point_node.current_time,
                "end_time": "Inf",
                "error_status": error_status,
                "path": "Нужна проводка",
                "info": ship['info'],
                "start_point": {
                    "lat": start_point_node.lat,
                    "lon": start_point_node.lon
                },
                "end_point": {
                    "lat": end_point_node.lat,
                    "lon": end_point_node.lon
                }
            },
        })
        with open('ship/ships_path.json', 'w', encoding='utf8') as f:
            json.dump(data, f, indent=4)
        #     line = folium.PolyLine(locations=shortest_path_array, color='blue', weight=5)
        #     line.add_to(m)
        # # Создаем линию, соединяющую отсортированные точки
        #
        # m.save('path_map.html')
        return -1

    def heuristic(n1, n2):
        return n1.time_in_path + n2.time_in_path

    # Вычисляем кратчайший путь с использованием алгоритма A*
    shortest_path = nx.astar_path(G, start_point_node, end_point_node, heuristic=heuristic)
    # print(shortest_path)

    # m = folium.Map(location=[25, 25], zoom_start=4)
    #
    # folium.Marker(location=(start_point_node.lat, start_point_node.lon), popup='Start Point').add_to(m)
    # folium.Marker(location=(start_point_node.end_lat, start_point_node.end_lon), popup='End Point').add_to(m)
    shortest_path_array = []
    shortest_path_array1 = []
    # if len(visited.rads) != 0:
    if len(visited.rads) != 0:
        for x in visited.rads:
            # edge = visited[(x, y)]
            shortest_path_array.append((x.center[0], x.center[1]))

        # line = folium.PolyLine(locations=shortest_path_array, color='blue', weight=5)
        # line.add_to(m)
    # Создаем линию, соединяющую отсортированные точки

    for x in shortest_path:
        # edge = visited[(x, y)]
        shortest_path_array1.append((x.lat, x.lon, x.current_time))
    # line = folium.PolyLine(locations=shortest_path_array1, color='black', weight=5)
    # line.add_to(m)
    # # Сохраняем карту
    # m.save('path_map.html')
    try:
        with open('ship/ships_path.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []


    data.append({
        generate_random_id(): {
            "name": ship['name'],
            "start_time": shortest_path_array1[0][2],
            "end_time": shortest_path_array1[0][-2],
            "path": [shortest_path_array1],
            "error_status": error_status,
            "info": ship['info'],
            "start_point": {
                "lat": start_point_node.lat,
                "lon": start_point_node.lon
            },
            "end_point": {
                "lat": end_point_node.lat,
                "lon": end_point_node.lon
            }
        },
    })
    with open('ship/ships_path.json', 'w') as f:
        json.dump(data, f, indent=4)
    return shortest_path_array1[-2].current_time


def generate_random_id():
    return str(uuid.uuid4())

# if __name__ == '__main__':
#
#     # with open(r'ship/ships.json', 'r', encoding='utf-8') as file:
#     #     ships = json.load(file)
#     #
#     # filtered_ships = [ship for ship in ships]
#
#     ice_map = Ice()
#     ship = get_ship_by_name("BORIS SOKOLOV", directory='/ship')
#     start_point = ship['start']
#     end_point = ship['end']
#     ship['class']="test"
#     with open('ship/info.json', 'r', encoding='utf-8') as file:
#         info = json.load(file)
#     info = info["test"]
#     ship['info'] = info
#     main(start_point, end_point, ship, ice_map)

    # for ship in filtered_ships:
    #     if ship['class'] == "Arc 9".strip():
    #         continue
    #     ship = get_ship_by_name(ship['name'], directory='/ship')
    #     start_point = ship['start']
    #     end_point = ship['end']
    #
    #     main(start_point, end_point, ship, ice_map)


if __name__ == '__main__':

    with open(r'ship/ships.json', 'r', encoding='utf-8') as file:
        ships = json.load(file)

    filtered_ships = [ship for ship in ships]

    ice_map = Ice()
    for ship in filtered_ships:
        if ship['class'] == "Arc 9".strip():
            continue
        ship = get_ship_by_name(ship['name'], directory='/ship')
        start_point = ship['start']
        end_point = ship['end']

        main(start_point, end_point, ship, ice_map)
