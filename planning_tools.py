import datetime
from datetime import datetime, timedelta
import heapq
from typing import List, Dict, Tuple, Optional
import itertools
import folium
from geopy.distance import geodesic
import networkx as nx
from search.testGenerateSteps import generate_points, optimize, check_start_end
from search.testMapMask import MapMask
from ship.getShip import get_ship_by_name
from helpers.nodeInfo import NodeInfo
import json
import math
import random
map_mask = MapMask('resultMap/map_image.png')
with open(r'ship/ports1.json', 'r', encoding='utf-8') as file:
    ports_df = json.load(file)

with open('ship/info.json', 'r', encoding='utf-8') as file:
    ice_info = json.load(file)

def get_port_coordinates(ports_df, port_name):
    # Ищем порт по имени
    for port in ports_df:
        if port['point_name'].upper() == port_name:
            return port['latitude'], port['longitude']


    
ice_dict = {
    "No ice class": (0,"No ice class"),"Ice1":(1,"Ice1"),
    "Ice2":(2, "Ice2"),
    "Ice3":(3,"Ice3"),
    "Arc4":(4,"Arc4"),
    "Arc5":(5,"Arc5"),
    "Arc6":(6,"Arc6"),
    "Arc7":(7,"Arc7"),
}


# Функция для преобразования даты в Unix время
# Чтение JSON файла
json_map_data_path = 'data\map_data.json'
with open(json_map_data_path, 'r') as file:
    maps_data = json.load(file)

        

'''
----------------------------------------------
Class for adding ship and storing ship info
----------------------------------------------
__init__ - add info about new ship
----------------------------------------------
'''
class Ship:

    def __init__(self, ship_id: int, destination: str, ready_date: datetime, ice_class: str, init_location: str, speed: int, ship_name: str):

        self.ship_id = ship_id
        self.init_location = init_location
        self.destination = destination
        self.ready_date = ready_date
        self.ice_class = ice_class

        self.is_departed = False

        self.speed = speed
        self.caravan = None
        self.ship_name = ship_name.upper()

'''
-------------------------------------------------
Class for adding icebreaker and storing it info 
-------------------------------------------------
__init__ - add info about new icebreaker
-------------------------------------------------
'''
class Icebreaker:
    def __init__(self, icebreaker_id: int, location: str, ice_class: int, speed: float,icebreaker_name: str, destination: str = None, available_date = datetime.combine(datetime.strptime("1-March-2022 00:00:00", "%d-%B-%Y %H:%M:%S").date(), datetime.min.time())):

        self.icebreaker_id = icebreaker_id
        self.location = location
        self.destination = destination
        self.is_departed = False
        self.available_date = available_date
        self.speed = speed
        self.ice_class = ice_class
        self.icebreaker_name=icebreaker_name

'''
------------------------------------------------------------------------------------------------------------------------
Class for adding sea port and storing it inforamtion  
------------------------------------------------------------------------------------------------------------------------
__init__                   - add info about new port
add_ship                   - add ship to port ships (new application recieved)
add_icebreaker             - add icebreaker to port (initial icebreaker location or new icebreaker arrived from trip)
add_arriving_icebreaker    - info about planning of icebreakers arrival to port including arriving date
remove_icebreaker          - remove icebreaker from port (icebreaker started trip from port)
remove_ship                - remove ship from port (ship started trip from port)
remove_arriving_icebreaker - remove icebreker from arrival list (has already arrived or plans changed)
------------------------------------------------------------------------------------------------------------------------
'''
class Port:
    def __init__(self, port_name: str):
        self.port_name = port_name
        self.ships: Dict[int, Ship] = {}
        self.icebreakers: Dict[int, Icebreaker] = {}
        self.arriving_icebreakers: Dict[int, Tuple[datetime.date, Icebreaker]] = {}

    def add_ship(self, ship: Ship):
        self.ships[ship.ship_id] = ship

    def add_icebreaker(self, icebreaker: Icebreaker):
        self.icebreakers[icebreaker.icebreaker_id] = icebreaker

    def add_arriving_icebreaker(self, icebreaker: Icebreaker, arriving_date: datetime):
        self.arriving_icebreakers[icebreaker.icebreaker_id] = [arriving_date, icebreaker]
    
    def remove_icebreaker(self, icebreaker: Icebreaker):
        self.icebreakers.pop(icebreaker.icebreaker_id, None)

    def remove_ship(self, ship: Ship):
        self.ships.pop(ship.ship_id, None)
    
    def remove_arriving_icebreaker(self, icebreaker: Icebreaker):
        self.arriving_icebreakers.pop(icebreaker.icebreaker_id, None)

'''
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Class for creating caravan from ships and storing caravan inforamtion  
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
__init__                      - create caravan from ships, calc departure date (latest ready-to-go date of all ships) + calc caravan quality value
calculate_caravan_quality     - return sum(for each ship((days for trip alone) - (days for trip as a part of caravan))) - if there is no way solo, time_profit = time_with_icebreaker
calculate_ship_travel_time    - return days for shortest trip from port A to port B for ship travelling solo considering ice conditions
calculate_caravan_travel_time - same as above, but for caravan, meaning with icebreaker
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
'''
class Caravan:
    def __init__(self, ships: List[Ship], icebreaker: Icebreaker, max_ships: int, planning_date: datetime):
        if len(ships) > max_ships:
            raise ValueError("too many ships in caravan")
        self.ships = ships
        self.start_location = ships[0].init_location
        self.end_location = ships[0].destination
        self.icebreaker = icebreaker
        self.is_departed = False
        self.departure_date = max(max(ship.ready_date for ship in ships),icebreaker.available_date)
        self.speed = min(ship.speed for ship in ships)
        self.planning_date = planning_date
        self.speed_coef = min([ice_dict[ship.ice_class.replace(' ', '')] for ship in ships], key=lambda x: x[0])[1]
        self.caravan_quality = self.calculate_caravan_quality()

    def calculate_caravan_quality(self):
        quality = 0
        time_with_icebreaker, path = calculate_caravan_travel_time(self)
        if time_with_icebreaker ==-1:return float('-inf')
        for ship in self.ships:
            time_alone, path = calculate_ship_travel_time(ship, self.planning_date)
            if time_alone == -1:
                time_profit = time_with_icebreaker
#            elif time_with_icebreaker == -1 and time_alone ==-1: quality = float('-inf')
            else:
                time_profit = time_alone - time_with_icebreaker
            quality += time_profit
        return quality


def calculate_ship_travel_time(ship: Ship, planning_date: datetime) -> int:
    print(ship.ship_name, ship.init_location, ship.destination)
    print(int(datetime.strptime( planning_date.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S').timestamp()))
    ship_inf = get_ship_by_name(ship.ship_name, directory='../ship')
    G = nx.Graph()
    current_time = int(datetime.strptime( ship.ready_date.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S').timestamp())
    # map_mask.change_ice_map(int(datetime.strptime( planning_date.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S').timestamp()))
    NodeInfo.set_class(ship_inf['end'][0], ship_inf['end'][1], current_time)
    start_point_node = check_start_end(map_mask, NodeInfo(ship_inf['start'][0], ship_inf['start'][1], 0., map_mask, current_time))
    end_point_node = check_start_end(map_mask, NodeInfo(ship_inf['end'][0], ship_inf['end'][1], 0, map_mask, current_time))

    G.add_node(start_point_node)
    G.add_node(end_point_node)

    steps = [start_point_node]
    visited = {}
    i = 0

    is_path_exist = False

    while True:
        if len(steps) == 0:
            print("пути нет")
            break
        current_point = steps.pop()
        if current_point.distance_to_end <= 10:
            print("Путь есть")
            is_path_exist = True
            G.add_edge(current_point, end_point_node)
            break
        if (current_point.x, current_point.y) in visited:
            continue
        visited[(current_point.x, current_point.y)] = current_point
        new_steps = generate_points(current_point, map_mask, visited, ship_inf['info'], 0, ship.speed)
        for step in new_steps:
            G.add_node(step)
            G.add_edge(current_point, step, weight=step.distance_to_end)
        steps.extend(new_steps)
        steps = sorted(steps, key=lambda x: x.distance_to_end, reverse=True)
        i += 1
        if i >= 10000:
            print("Достигнут предел итераций")
            break

    # G.add_edge(current_point, end_point_node)

    # Функция эвристики для алгоритма A*
    def heuristic(n1, n2):
        return n1.time_in_path + n2.time_in_path
    if is_path_exist:
        shortest_path = nx.astar_path(G, start_point_node, end_point_node, heuristic=heuristic)
        print(shortest_path[-2].current_time, (shortest_path[-2].current_time-int(datetime.strptime( ship.ready_date.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S').timestamp()))/(3600*24))
        return (shortest_path[-2].current_time-int(datetime.strptime( ship.ready_date.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S').timestamp()))/(3600*24), shortest_path
    return -1, []



def calculate_caravan_travel_time(caravan: Caravan) -> int:
    G = nx.Graph()

    current_time = int(datetime.strptime( caravan.departure_date.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S').timestamp())
    # map_mask.change_ice_map(int(datetime.strptime( caravan.planning_date.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S').timestamp()))

    print(caravan.start_location, caravan.end_location, [ship.ship_name for ship in caravan.ships], current_time)
    print(int(datetime.strptime( caravan.planning_date.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S').timestamp()))

    NodeInfo.set_class(get_port_coordinates(ports_df=ports_df, port_name=caravan.end_location)[0], get_port_coordinates(ports_df=ports_df, port_name=caravan.end_location)[1], current_time)

    start_point_node = check_start_end(map_mask, NodeInfo(get_port_coordinates(ports_df=ports_df, port_name=caravan.start_location)[0], get_port_coordinates(ports_df=ports_df, port_name=caravan.start_location)[1], 0., map_mask, current_time))
    end_point_node = check_start_end(map_mask, NodeInfo(get_port_coordinates(ports_df=ports_df, port_name=caravan.end_location)[0], get_port_coordinates(ports_df=ports_df, port_name=caravan.end_location)[1], 0, map_mask, current_time))

    G.add_node(start_point_node)
    G.add_node(end_point_node)

    steps = [start_point_node]
    visited = {}
    i = 0

    is_path_exist = False

    while True:
        if len(steps) == 0:
            print("пути нет")
            break
        current_point = steps.pop()
        if current_point.distance_to_end <= 10:
            print("Путь есть")
            is_path_exist = True
            G.add_edge(current_point, end_point_node)
            break
        if (current_point.x, current_point.y) in visited:
            continue
        visited[(current_point.x, current_point.y)] = current_point
        new_steps = generate_points(current_point, map_mask, visited, ice_info[caravan.speed_coef],1,caravan.speed)
        for step in new_steps:
            G.add_node(step)
            G.add_edge(current_point, step, weight=step.distance_to_end)
        steps.extend(new_steps)
        steps = sorted(steps, key=lambda x: x.distance_to_end, reverse=True)
        i += 1
        if i >= 10000:
            print("Достигнут предел итераций")
            break

    # G.add_edge(current_point, end_point_node)

    # Функция эвристики для алгоритма A*
    def heuristic(n1, n2):
        return n1.time_in_path + n2.time_in_path

    if is_path_exist:
        shortest_path = nx.astar_path(G, start_point_node, end_point_node, heuristic=heuristic)
        print(shortest_path[-2].current_time, (shortest_path[-2].current_time-int(datetime.strptime( caravan.departure_date.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S').timestamp()))/(3600*24))
        return (shortest_path[-2].current_time-int(datetime.strptime( caravan.departure_date.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S').timestamp()))/(3600*24), shortest_path
    return -1, []

def draw_path(shortest_path, map_mask):
    shortest_path_array = []
    origin_path = []
    for edge in shortest_path:
        origin_path.append((edge.lat, edge.lon))
    for edge in shortest_path:
        shortest_path_array.append((edge.lat, edge.lon))
    map_mask.plot_graph_on_map(shortest_path_array)
    



def calculate_centroid(coordinates):
    x = 0
    y = 0
    z = 0

    for lat, lon in coordinates:
        latitude = math.radians(lat)
        longitude = math.radians(lon)
        x += math.cos(latitude) * math.cos(longitude)
        y += math.cos(latitude) * math.sin(longitude)
        z += math.sin(latitude)

    total = len(coordinates)

    x = x / total
    y = y / total
    z = z / total

    central_lon = math.atan2(y, x)
    hyp = math.sqrt(x * x + y * y)
    central_lat = math.atan2(z, hyp)

    return (math.degrees(central_lat), math.degrees(central_lon))

def find_water_point(lat, lon, step_size=0.1, max_attempts=1000):
    for _ in range(max_attempts):
        x,y = map_mask.decoder(lat, lon)
        if map_mask.is_aqua(x,y):
            return (lat, lon)
        
        # Пробуем сместиться на небольшое расстояние в случайном направлении
        angle = random.uniform(0, 2 * math.pi)
        lat += step_size * math.cos(angle)
        lon += step_size * math.sin(angle)
    
    raise Exception("Не удалось найти точку на воде")
    

def find_closest_meeting_point(ships:list):
    ship_inf = [get_ship_by_name(ship.ship_name, directory='../ship') for  ship in ships]
    coordinates = [(ship_inf_i['start'][0], ship_inf_i['start'][1]) for ship_inf_i in ship_inf]
    for i in coordinates: print(f'{i[1]},{i[0]}')
    center_lat, center_lon = calculate_centroid(coordinates)
    coordinates.append(find_water_point(center_lat, center_lon))
    map_mask.plot_graph_on_map(coordinates)
    return find_water_point(center_lat, center_lon)


'''
----------------------------------------------------------------------------------------------
Class for storing planned routes, dates and included ships
----------------------------------------------------------------------------------------------
add_route          - add new planned route with all required info about it
get_routes_by_date - return all routes planned for current date (departing/arriving)
----------------------------------------------------------------------------------------------
'''
class RouteSchedule:
    def __init__(self):
        self.routes = []

    def add_route(self, departure_date: datetime, arrival_date: datetime, 
                  departure_port: str, arrival_port: str, movement_type: str, 
                  participants: List[str], quality, path):
        route = {
            'departure_date': departure_date,
            'quality': quality,
            'arrival_date': arrival_date,
            'departure_port': departure_port,
            'arrival_port': arrival_port,
            'movement_type': movement_type,
            'participants': participants,
            'is_finished': False,
            'path':path
        }
        self.routes.append(route)

    def get_routes_by_date(self, date: datetime) -> List[Dict]:
        return [route for route in self.routes if route['departure_date'].date() <= date.date() or route['arrival_date'].date() == date.date()]
    
    def update_route(self, departure_date: datetime, arrival_date: datetime, 
                  departure_port: str, arrival_port: str, movement_type: str, participants: List[str], quality, path):
        found = False
        for i, route in enumerate(self.routes):
            if route["movement_type"] == 'icebreaker' or movement_type == 'icebreaker': continue
            if route["movement_type"] == 'caravan': 
                old_participants = set([ship.ship_name for ship in route['participants'][:-1]])
            elif route["movement_type"] == 'ship': 
                old_participants=set(route['participants'].ship_name)
            if movement_type == 'caravan': 
                new_participants = set([ship.ship_name for ship in participants[:-1]])
            elif movement_type == 'ship': 
                new_participants=set(participants.ship_name)
            if len(set.intersection(new_participants, old_participants))>0 and quality > route['quality']:
                self.routes.pop(i)
                self.add_route(departure_date,arrival_date,departure_port,arrival_port, movement_type, participants, quality)
                break
        if not found:
            self.add_route(departure_date,arrival_date,departure_port,arrival_port, movement_type, participants, quality, path)
            
    def print_schedule(self):
        for rout in self.routes:
            participants = None
            if rout["movement_type"] == 'icebreaker': 
                participants = rout['participants'].icebreaker_id
            elif rout["movement_type"] == 'caravan': 
                participants = [ship.ship_name for ship in rout['participants'][:-1]]+ [rout['participants'][-1].icebreaker_id]
            elif rout["movement_type"] == 'ship': 
                participants = rout['participants'].ship_name
            print('departure_date:', rout['departure_date'],
            'quality:', rout['quality'],
            'arrival_date:', rout['arrival_date'],
            'departure_port:', rout['departure_port'],
            'arrival_port:', rout['arrival_port'],
            'movement_type:', rout["movement_type"],
            'participants:', participants)

    def save_schedule_json(self):
        fin_dict = {}
        for i, rout in enumerate(self.routes):
            
            cur_dict = {}

            participants = None
            if rout["movement_type"] == 'icebreaker': 
                participants = rout['participants'].icebreaker_id
            elif rout["movement_type"] == 'caravan': 
                participants = [ship.ship_name for ship in rout['participants'][:-1]]+ [rout['participants'][-1].icebreaker_id]
            elif rout["movement_type"] == 'ship': 
                participants = rout['participants'].ship_name

            print('departure_date:', rout['departure_date'],
            'quality:', rout['quality'],
            'arrival_date:', rout['arrival_date'],
            'departure_port:', rout['departure_port'],
            'arrival_port:', rout['arrival_port'],
            'movement_type:', rout["movement_type"],
            'participants:', participants)
            
            cur_dict['participants'] = participants
            cur_dict['departure_date'] = rout['departure_date'].strftime('%Y-%m-%d %H:%M:%S')
            cur_dict['arrival_date'] = rout['arrival_date'].strftime('%Y-%m-%d %H:%M:%S')
            cur_dict['departure_port'] = rout['departure_port']
            cur_dict['arrival_port'] = rout['arrival_port']
            cur_dict['movement_type'] = rout['movement_type']
            cur_dict['quality'] = rout['quality']
            cur_dict['path']=[[node.lat,node.lon,node.current_time] for node in rout['path']]
            
            fin_dict[i] = cur_dict


        with open('routes_schedule.json', 'w') as file:
            json.dump(fin_dict, file)


'''
------------------------------------------------------------------------------------------------------------------------------
Class for whole planning process
------------------------------------------------------------------------------------------------------------------------------
__init__                   - initialize parameters for system
run_daily_planning         - daily iteration for schedule, planning and ships status update
check_new_applications     - adding application online
check_ice_conditions       - check ice condition changes
optimize_routes            - routes optimization for ships that are already on route (can be triggered by ice changes)
plan_shipments             - departure planning with/without icebreaker for each port
plan_caravan_shipment      - if there are icebreakers in port, plan caravan shipment
group_ships_by_destination - group ships from one port 
find_best_caravan          - find most time-profitable combination of ships to form a caravan with cur icebreaker
check_icebreaker_availability - find if icebreaker is needed somewhere more than in current port, if so - plans it departure there
reassign_icebreaker - planning icebreaker solo departure to a more-time-profitable port, adding plan to schedule
plan_remaining_ships - plan departure for ships that were not included in the best caravans departures
record_route - add planned route (caravan/ship/icebreaker) to schedule
update_schedule - daily schedule updating. If today there are some shipments - trigger all statuses updating
handle_departure - update all ships and port statuses triggered by departures (caravan/ship/icebreaker)
handle_arrival - update all ships and port statuses triggered by arrival (caravan/ship/icebreaker)
calculate_icebreaker_travel_time_to_port - calculate icebreaker days in solo trip from port A to port B
------------------------------------------------------------------------------------------------------------------------------
'''
class PlanningSystem:
    def __init__(self, ports: List[Port], max_in_caravan: int, max_icebreakers: int, current_date: datetime):
        self.ports = {port.port_name: port for port in ports}
        self.max_in_caravan = max_in_caravan
        self.max_icebreakers = max_icebreakers
        self.current_date = current_date
        self.schedule = RouteSchedule()
        self.cur_time_range = "1646254800-1646859600"

    def run_daily_planning(self):
        got_new_applications = True
        ice_conditions_changed = True
        is_planning_finished = False
        new_icebreaker_arrivals = False
        while not is_planning_finished:
            
            if got_new_applications or ice_conditions_changed or new_icebreaker_arrivals:
                self.optimize_routes()
                self.plan_shipments()

            new_icebreaker_arrivals = self.update_schedule()

            self.current_date += timedelta(days=1)
            print('LOG current date: ', self.current_date)

            #got_new_applications = self.check_new_applications()
            ice_conditions_changed = self.check_ice_conditions()
            is_planning_finished = self.check_planning_finish()

    def check_new_applications(self):
        # Check for new ship applications and add them to respective ports     
        print('Want to add new shipment application? Respond y/n: ')

        while True:
            new_application = input()
            if new_application == 'y':
                print('Insert ship info step-by-step')
                while True:
                    try:
                        print('Type ship id: ')
                        ship_id = int(input())
                        print('Type ship destination: ')
                        destination = input().upper()
                        print('Type ship ready date in format 2010-06-12 00:00:00 : ')
                        ready_date = datetime.strptime(input(),'%Y-%m-%d %H:%M:%S')
                        print('Type department ice_class (Arc4-Arc7, нет): ')
                        ice_class = input()
                        print('Type ship init location: ')
                        init_location = input().upper()
                        print('Type ship speed: ')
                        speed = int(input())
                        print('Type ship name: ')
                        ship_name = input()                    

                        new_ship = Ship(ship_id=ship_id, destination=destination, ready_date=ready_date, ice_class=ice_class,
                                        init_location=init_location,speed=speed, ship_name=ship_name)
                        
                        self.ports[init_location].add_ship(new_ship)
                        break 
                    except:
                        while True:
                            print('Wrong input format. Want to try again? y/n')
                            try_again = input()
                            if try_again == 'n':
                                return False
                            elif try_again=='y':
                                break
                            else:
                                print('Wrong y/n format. Type y or n')
                return True
            elif new_application == 'n':
                return False
            else:
                print('Wrong input format. Type y or n')
                continue


    def check_ice_conditions(self):
        # Check for changes in ice conditions and update routes if necessary
        new_timerange = ''
        current_date = int(datetime.strptime( self.current_date.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S').timestamp())
        # Поиск подходящего диапазона времени
        for time_range, file_path in maps_data.items():
            start_time, end_time = map(int, time_range.split('-'))
            if start_time <= current_date < end_time:
                new_timerange = time_range
                break
        if current_date< int(min(maps_data.keys(), key=lambda x:  int(x.split('-')[0])).split('-')[0]): 
            new_timerange = "1646254800-1646859600"
        elif current_date> int(max(maps_data.keys(), key=lambda x:  int(x.split('-')[1])).split('-')[0]):
            new_timerange = "1653512400-1646859600"
        
        if self.cur_time_range != new_timerange:
            self.cur_time_range = new_timerange
            return True
        
        return False
        


    def check_planning_finish(self):
        # check if there are some unfinished routes
        for route in self.schedule.routes:
            if route['arrival_date'] > self.current_date:
                return False
            
        # check if there are some port with ships
        for port in self.ports.values():
            if port.ships:
                return False
        return True

    def optimize_routes(self):
        # Optimize routes for all ships and icebreakers considering new conditions
        # calculate new best path for all ongoing icebreakers
        pass

    def plan_shipments(self):
        for port in self.ports.values():
            if port.icebreakers:
                self.plan_caravan_shipment(port)
        
        for port in self.ports.values():
            self.check_icebreaker_availability(port)
            self.plan_remaining_ships(port)

    def plan_caravan_shipment(self, port: Port):
        # Step 1: Group ships by destination
        destination_groups = self.group_ships_by_destination(list(port.ships.values()))

        # Step 2: Form caravans for each destination group
        for destination, ships in destination_groups.items():
            best_caravan = self.find_best_caravan(ships, list(port.icebreakers.values()))

            if best_caravan:
                # Set departure and arrival dates
                travel_time,path = calculate_caravan_travel_time(best_caravan)
                arrival_date = best_caravan.departure_date + timedelta(days=travel_time)

                best_caravan.icebreaker.available_date = arrival_date

                participants = [ship for ship in best_caravan.ships] + [best_caravan.icebreaker]
                self.record_route(departure_date=best_caravan.departure_date, 
                                quality=best_caravan.caravan_quality,  

                                arrival_date=arrival_date, 
                                departure_port=port.port_name,
                                arrival_port=best_caravan.ships[0].destination, 
                                movement_type='caravan',
                                participants=participants,
                                path=path)             


    def group_ships_by_destination(self, ships: List[Ship]) -> Dict[str, List[Ship]]:
        groups = {}
        for ship in ships:
            if ship.destination not in groups:
                groups[ship.destination] = []
            groups[ship.destination].append(ship)
        return groups

    def find_best_caravan(self, ships: List[Ship], icebreakers: List[Icebreaker]) -> Optional[Caravan]:
        best_caravan = None
        best_quality = float('-inf')

        # Generate all possible combinations of ships for sizes from 1 to max_in_caravan
        for size in range(1, min(self.max_in_caravan, len(ships)) + 1):
            for comb in itertools.combinations(ships, size):
                if None in comb:
                    continue
                for icebreaker in icebreakers:
                    caravan = Caravan(list(comb), icebreaker, self.max_in_caravan, planning_date=self.current_date)
                    if caravan.caravan_quality > best_quality:
                        best_caravan = caravan
                        best_quality = caravan.caravan_quality
                        print(best_caravan.caravan_quality)
        if best_caravan and best_caravan.caravan_quality>float('-inf'):
            return best_caravan 


    def check_icebreaker_availability(self, port: Port):
        for icebreaker in port.icebreakers.values():
            if icebreaker.available_date <= self.current_date:
                best_port, best_value = None, float('-inf')

                if port.ships:
                    best_caravan = self.find_best_caravan(list(port.ships.values()), list(port.icebreakers.values()))
                    best_value = best_caravan.caravan_quality if best_caravan else float('-inf')

                for other_port in self.ports.values():
                    if other_port == port:
                        continue
                    best_caravan = self.find_best_caravan(list(other_port.ships.values()), list(port.icebreakers.values()))
                    if best_caravan:
                        travel_time, path = self.calculate_icebreaker_travel_time_to_port(icebreacker=icebreaker, from_port=port,to_port=other_port)
                        if travel_time == -1:
                            port_value = float('-inf')
                        else:
                            time_before_caravan_ready = (best_caravan.departure_date - self.current_date).days
                            port_value = best_caravan.caravan_quality - abs(travel_time - time_before_caravan_ready)

                        if port_value > best_value:
                            best_port, best_value = other_port, port_value
                if best_port:
                    self.reassign_icebreaker(port, best_port, icebreaker, best_value)

    def reassign_icebreaker(self, port: Port, best_port: Port, icebreaker: Icebreaker, quality: float):
        
        travel_time, path = self.calculate_icebreaker_travel_time_to_port(icebreacker=icebreaker,from_port=port, to_port=best_port)
        arrival_date = self.current_date + timedelta(days=travel_time)
        
        self.record_route(departure_date=self.current_date,
                          quality=quality, 
                          arrival_date=arrival_date, 
                          departure_port=port.port_name,
                          arrival_port=best_port.port_name, 
                          movement_type='icebreaker',
                          participants=icebreaker,
                          path=path)
    
    def plan_remaining_ships(self, port: Port):
        for ship in port.ships.values():
            # Check if the ship is part of a second-best caravan
            # ... add logic for second-best caravan check -- if not smth else (???)

            # If not, assign independent departure date
            departure_date = ship.ready_date
            travel_time, path = calculate_ship_travel_time(ship, planning_date=self.current_date)
            if travel_time != -1:
                arrival_date = departure_date + timedelta(days=travel_time)
                
                self.record_route(departure_date=departure_date, 
                                  quality=0,

                                  arrival_date=arrival_date, 
                                  departure_port=port.port_name,
                                  arrival_port=ship.destination, 
                                  movement_type='ship',

                                  participants=ship,
                                  path=path)    


# insert some logs somewhere, like:
#print(f"[LOG] Caravan with icebreaker {caravan.icebreaker.icebreaker_id} departs from {port.port_name} on {caravan.departure_date} to {caravan.ships[0].destination} arriving at {arrival_date}.")
    
    def record_route(self, departure_date: datetime, arrival_date: datetime, 
                     departure_port: str, arrival_port: str, movement_type: str, 
                     participants: List[str], quality:float, path):
        
        self.schedule.update_route(departure_date=departure_date,
                                quality= quality,
                                arrival_date=arrival_date, 
                                departure_port=departure_port,
                                arrival_port=arrival_port, 
                                movement_type=movement_type, 
                                participants=participants,
                                path=path)
        print(departure_date, arrival_date, departure_port,arrival_port, movement_type, participants)
        
        
    def update_schedule(self):
        routes_today = self.schedule.get_routes_by_date(self.current_date)
        new_available_icebreaker = False
        for route in routes_today:
            if not route['is_finished']:
                if route['movement_type'] == 'icebreaker' or route['movement_type'] == 'ship':
                    is_departed = route['participants'].is_departed
                else:
                    is_departed = route['participants'][0].is_departed

                if route['departure_date'].date() <= self.current_date.date() and not is_departed:
                    # Handle departure
                    self.handle_departure(route)
                elif route['arrival_date'].date() == self.current_date.date():
                    # Handle arrival
                    new_available_icebreaker = self.handle_arrival(route)
                else:
                    print(f'WARNING: Can not handle route. Date: {self.current_date}. Route: {route}')
        return new_available_icebreaker

    def handle_departure(self, route: Dict):
        port = self.ports[route['departure_port']]
        destination_port = self.ports[route['arrival_port']]
        if route['movement_type'] == 'caravan':
            for participant in route['participants']:
                if isinstance(participant, Ship):
                    participant.is_departed = True
                    port.remove_ship(participant)
                elif isinstance(participant, Icebreaker):
                    participant.is_departed = True
                    port.remove_icebreaker(participant)
                    participant.current_port = None
                    destination_port.add_arriving_icebreaker(participant, route['arrival_date'])
        elif route['movement_type'] == 'icebreaker':
            icebreaker = route['participants'] 
            if isinstance(icebreaker, Icebreaker):
                icebreaker.is_departed = True
                port.remove_icebreaker(icebreaker)
                icebreaker.current_port = None
                destination_port.add_arriving_icebreaker(icebreaker, route['arrival_date'])
        elif route['movement_type'] == 'ship':

            ship = route['participants']  # Предполагается, что ship один в списке
            if isinstance(ship, Ship):
                ship.is_departed = True
                port.remove_ship(ship)

    def handle_arrival(self, route: Dict):
        port = self.ports[route['arrival_port']]
        is_icebreaker = False

        if route['movement_type'] == 'caravan':
            for participant in route['participants']:
                if isinstance(participant, Icebreaker):
                    participant.is_departed = False
                    port.add_icebreaker(participant)
                    port.remove_arriving_icebreaker(participant)
                    is_icebreaker = True  # Icebreaker должен быть один, поэтому можно прервать цикл

        elif route['movement_type'] == 'icebreaker':
            participant = route['participants']
            if isinstance(participant, Icebreaker):
                participant.is_departed = False
                port.add_icebreaker(participant)
                port.remove_arriving_icebreaker(participant)
                is_icebreaker = True  # Icebreaker должен быть один, поэтому можно прервать цикл
        route['is_finished'] = True
        return is_icebreaker

    def calculate_icebreaker_travel_time_to_port(self, icebreacker: Icebreaker,from_port: Port, to_port: Port) -> int:
        G = nx.Graph()
        current_time = int(datetime.strptime( self.current_date.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S').timestamp())
        map_mask.change_ice_map(int(datetime.strptime( self.current_date.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S').timestamp()))
        print(from_port.port_name, to_port.port_name,  icebreacker.icebreaker_name,current_time)
        NodeInfo.set_class(get_port_coordinates(ports_df=ports_df, port_name=to_port.port_name)[0], get_port_coordinates(ports_df=ports_df, port_name=to_port.port_name)[1], current_time)
        start_point_node = check_start_end(map_mask, NodeInfo(get_port_coordinates(ports_df=ports_df, port_name=from_port.port_name)[0], get_port_coordinates(ports_df=ports_df, port_name=from_port.port_name)[1], 0., map_mask, current_time))
        end_point_node = check_start_end(map_mask, NodeInfo(get_port_coordinates(ports_df=ports_df, port_name=to_port.port_name)[0], get_port_coordinates(ports_df=ports_df, port_name=to_port.port_name)[1], 0, map_mask, current_time))
        G.add_node(start_point_node)
        G.add_node(end_point_node)

        steps = [start_point_node]
        visited = {}
        i = 0

        is_path_exist = False

        while True:
            if len(steps) == 0:
                print("пути нет")
                break
            current_point = steps.pop()
            if current_point.distance_to_end <= 10:
                print("Путь есть")
                is_path_exist = True
                G.add_edge(current_point, end_point_node)
                break
            if (current_point.x, current_point.y) in visited:
                continue
            visited[(current_point.x, current_point.y)] = current_point
            new_steps = generate_points(current_point, map_mask, visited, ice_info['Arc9'][icebreacker.icebreaker_name],1,1)
            for step in new_steps:
                G.add_node(step)
                G.add_edge(current_point, step, weight=step.distance_to_end)
            steps.extend(new_steps)
            steps = sorted(steps, key=lambda x: x.distance_to_end, reverse=True)
            i += 1
            if i >= 10000:
                print("Достигнут предел итераций")
                break

        # G.add_edge(current_point, end_point_node)

        # Функция эвристики для алгоритма A*
        def heuristic(n1, n2):
            return n1.time_in_path + n2.time_in_path


        if is_path_exist:
            shortest_path = nx.astar_path(G, start_point_node, end_point_node, heuristic=heuristic)
            optimize(shortest_path, map_mask, info, 0, ship['speed'])
            print(shortest_path[-2].current_time, (shortest_path[-2].current_time-int(datetime.strptime( self.current_date.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S').timestamp()))/(3600*24))
            return (shortest_path[-2].current_time-int(datetime.strptime( self.current_date.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S').timestamp()))/(3600*24), shortest_path
        return -1, []

