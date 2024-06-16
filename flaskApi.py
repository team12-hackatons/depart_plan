import json
from datetime import datetime
from random import random, randint
from flask_cors import CORS, cross_origin
from flask import Flask, jsonify, request
from planning_tools import calculate_ship_travel, Ship

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

with open('data/routes_schedule.json', 'r', encoding='utf-8') as f:
    ships = json.load(f)

@app.route('/api/ships', methods=['GET'])
@cross_origin()
def getAllShips():
    filtered_ships = {}

    for key, ship in ships.items():
        # Exclude the 'path' field from each ship
        filtered_ship = {k: v for k, v in ship.items() if k != 'path'}
        filtered_ships[key] = filtered_ship

    return jsonify(filtered_ships)

@app.route('/api/ship/<string:name>', methods=['GET'])
@cross_origin()
def getOneShip(name):
    if name in ships:
        response = jsonify(ships[name])
        response.headers.add('Content-Type', 'application/json; charset=utf-8')
        return response
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



