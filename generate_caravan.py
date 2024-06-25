import json

from geopy.distance import geodesic

from helpers.build_tree import Ice

class Caravan:
    def __init__(self, info, point):
        self.info = info
        self.ships =[]
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

        return sorted_data


    filtered_and_sorted_data = filter_and_sort_ships(data)


    print(json.dumps(filtered_and_sorted_data, ensure_ascii=False, indent=4))
    # ice_map = Ice()
    while True:
        currentShip = filtered_and_sorted_data.pop()
        cc = None
        km = 922337203685477580
        id_key = next(iter(currentShip))
        for icebreaker in caravan_dict.values():
            kms = geodesic((currentShip[id_key]['start_point']['lat'], currentShip[id_key]['start_point']['lon']), (icebreaker.point['latitude'], icebreaker.point['longitude'])).kilometers
            if cc is None or km > kms:
                km = kms
                cc = icebreaker
        if km == 0:
            cc.add_ship()
        # else:
        #     main()