import json

from geopy.distance import geodesic
from ship.getShip import get_ship_by_name
from helpers.build_tree import Ice
from helper import main


class Caravan:
    def __init__(self, info, point):
        self.info = info
        self.ships = []
        self.current_time = 0
        self.point = point
        self.max_ships = 3
        self.paths = []

    def add_ship(self, ship_id):
        if len(self.ships) == self.max_ships:
            return False
        with open('ship/ships_path.json', 'r') as f:
            data = json.load(f)
        ship = data[ship_id]


def add_ship_to_caravan(ship, ice_map):
    min_time = 922337203685477580
    current_icebreaker = None
    for icebreaker in caravan_dict:
        icebreaker = caravan_dict[icebreaker]
        time = main((icebreaker.point['latitude'], icebreaker.point['longitude']), (ship['start_point']['lat'], ship['start_point']['lon']), icebreaker, ice_map) + icebreaker.current_time
        time += icebreaker.current_time
        if ship['start_time'] > time:
            time = ship['start_time']
        if min_time == time:
            km1 = geodesic((currentShip['start_point']['lat'], currentShip['start_point']['lon']), (
            icebreaker.point['latitude'], icebreaker.point['longitude'])).kilometers

            km2 = geodesic((currentShip['start_point']['lat'], currentShip['start_point']['lon']), (
            current_icebreaker.point['latitude'], current_icebreaker.point['longitude'])).kilometers

            if km1 < km2:
                current_icebreaker = icebreaker
        elif min_time > time:
            min_time = time
            current_icebreaker = icebreaker


if __name__ == '__main__':
    try:
        with open('ship/ships_path.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        ValueError("generate_path_from generate_path_for_all_ships.py")

    try:
        with open('ship/ice_breaker_state.json', 'r') as f:
            ice_breakers = json.load(f)
    except FileNotFoundError:
        ValueError("generate_path_from generate_path_for_all_ships.py")

    caravan_dict = {}
    for icebreaker in ice_breakers:
        print(icebreaker)
        caravan_dict[icebreaker] = Caravan(ice_breakers[icebreaker]['info'], ice_breakers[icebreaker]['position'])


    def filter_and_sort_ships(data):
        filtered_data = []

        for item in data:
            for key, value in item.items():
                if value["error_status"] != 0:
                    filtered_data.append({key: value})

        sorted_data = sorted(filtered_data, key=lambda x: list(x.values())[0]["start_time"])
        ships = []
        for data in sorted_data:
            id_key = next(iter(data))
            ships.append(data[id_key])
        return ships


    filtered_and_sorted_data = filter_and_sort_ships(data)


    print(json.dumps(filtered_and_sorted_data, ensure_ascii=False, indent=4))

    ice_map = Ice()
    while True:
        currentShip = filtered_and_sorted_data.pop()
        add_ship_to_caravan(currentShip, ice_map)




