import json
import os


def get_ship_by_name(name, directory=r'ship'):
    # try:
        with open(r'ship\ships.json', 'r', encoding='utf-8') as file:
            ships = json.load(file)
        with open(r'ship\ports1.json', 'r', encoding='utf-8') as file:
            ports = json.load(file)
        with open('ship\info.json', 'r', encoding='utf-8') as file:
            info = json.load(file)
        res = None
        for ship in ships:
            if ship['name'].upper() == name.upper():
                res = ship
                break
        class_ship = res['class'].replace(' ', '')
        info = info[class_ship]
        res['info'] = info
        start, end = None, None
        for port in ports:
            if port['point_name'].upper() == res['start'].upper():
                start = (port['latitude'], port['longitude'])
            if port['point_name'].upper() == res['end'].upper():
                end = (port['latitude'], port['longitude'])
        res['start'] = start
        res['end'] = end
        return res
    # except:
    #     print("Корабль не найден.")
    #     return None

