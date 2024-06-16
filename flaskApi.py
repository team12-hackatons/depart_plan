import json
from datetime import datetime
from random import random, randint
from flask_cors import CORS, cross_origin
from flask import Flask, jsonify, request
from planning_tools import calculate_ship_travel, Ship

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Пример данных о кораблях (замените на ваше хранилище данных)
ships = [
    {
        "name": "Ship1",
        "ice_class": "A",
        "start_point": "Port A",
        "end_point": "Port B",
        "start_time": "2024-06-16 12:00:00"
    },
    {
        "name": "Ship2",
        "ice_class": "B",
        "start_point": "Port C",
        "end_point": "Port D",
        "start_time": "2024-06-16 13:00:00"
    }
]

@app.route('/api/ships', methods=['GET'])
@cross_origin()
def getAllShips():
    return jsonify(ships)

@app.route('/api/ship/<string:name>', methods=['GET'])
@cross_origin()
def getOneShip(name):
    for ship in ships:
        if ship['name'] == name:
            return jsonify(ship)
    return jsonify({'message': 'Ship not found'}), 404

# Добавление нового корабля (POST запрос)
@app.route('/api/addShip', methods=['POST'])
@cross_origin()
def addShip():
    with open('ship/info.json', 'r', encoding='utf-8') as file:
        info = json.load(file)
    info = info[request.json['ice_class']]

    new_ship = {
        "ship_name": request.json['ship_name'],
        # "init_location": request.json['init_location'],
        # "destination": request.json['destination'],
        "end": request.json['end'],
        "start": request.json['start'],
        "speed": request.json['speed'],
        "ready_date": datetime.fromisoformat(request.json['ready_date'])
    }
    # ships.append(new_ship)
    res = calculate_ship_travel(new_ship, new_ship['ready_date'], info)[1]
    nodes_list = [
        {
            'lat': node.lat,
            'lon': node.lon,
            'current_time': node.current_time
        }
        for node in res
    ]

    return jsonify(nodes_list), 200

@app.route('/api/currentPosition', methods=['POST'])
@cross_origin()
def getCurrentPosition():
    ship_name = request.json['name']
    current_time = request.json['current_time']
    return jsonify({'message': f'Current position of {ship_name} at {current_time}'}), 200

if __name__ == '__main__':
    app.run(debug=True)



