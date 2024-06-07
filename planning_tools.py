import datetime
import heapq
from typing import List, Dict, Tuple

class Ship:
    def __init__(self, ship_id: int, destination: str, ready_date: datetime.date, ice_class: int, init_location: str):
        self.ship_id = ship_id
        self.init_location = init_location
        self.destination = destination
        self.ready_date = ready_date
        self.ice_class = ice_class
        self.caravan = None

class Icebreaker:
    def __init__(self, icebreaker_id: int, location: str, destination: str, available_date: datetime.date, ice_class: int):
        self.icebreaker_id = icebreaker_id
        self.location = location
        self.destination = destination
        self.available_date = available_date
        self.ice_class = ice_class

class Port:
    def __init__(self, port_name: str):
        self.port_name = port_name
        self.ships = []
        self.icebreakers = []
        self.arrival_dates = {}             # mb delete

    def add_ship(self, ship: Ship):
        self.ships.append(ship)

    def add_icebreaker(self, icebreaker: Icebreaker):
        self.icebreakers.append(icebreaker)
    
    def remove_icebreaker(self, icebreaker: Icebreaker):
        self.icebreakers.pop(icebreaker)

    def remove_ship(self, ship: Ship):
        self.ships.pop(ship)

class Caravan:
    def __init__(self, ships: List[Ship], icebreaker: Icebreaker, max_ships: int):
        if len(ships) > max_ships:
            print("too much ships in caravan")
            return 0
        self.ships = ships
        self.icebreaker = icebreaker
        self.departure_date = max(ship.ready_date for ship in ships)
        self.caravan_quality = self.calculate_caravan_quality()

    def calculate_caravan_quality(self):
        quality = 0
        for ship in self.ships:
            time_alone = calculate_travel_time(ship, None)
            time_with_icebreaker = calculate_travel_time(ship, self.icebreaker)
            time_profit = time_alone - time_with_icebreaker
            quality += time_profit
        return quality

def calculate_travel_time(ship: Ship, icebreaker: Icebreaker) -> int:
    # Placeholder for travel time calculation function
    # returns travel time in days
    pass


class PlanningSystem:
    def __init__(self, ports: List[Port], max_in_caravan: int, max_icebreakers: int, current_date: datetime.date):
        self.ports = {port.port_name: port for port in ports}
        self.max_in_caravan = max_in_caravan
        self.max_icebreakers = max_icebreakers
        self.current_date = current_date

    def run_daily_planning(self):
        while True:
            self.current_date += datetime.timedelta(days=1)
            self.check_new_applications()
            self.check_ice_conditions()

            # if need_to_plan() or need_to_optimize():
            self.optimize_routes()
            self.plan_shipments()

    def check_new_applications(self):
        # Check for new ship applications and add them to respective ports
        # some function to add applications online
        pass

    def check_ice_conditions(self):
        # Check for changes in ice conditions and update routes if necessary
        # some function to check changes in ice
        pass

    def optimize_routes(self):
        # Optimize routes for all ships and icebreakers considering new conditions
        # calculate new best path for all ongoing icebreakers
        pass

    def plan_shipments(self):
        for port_name, port in self.ports.items():
            self.plan_port_shipments(port)

    def plan_port_shipments(self, port: Port):
        # Step 1: Group ships by destination
        destination_groups = self.group_ships_by_destination(port.ships)

        # Step 2: Form caravans for each destination group
        for destination, ships in destination_groups.items():
            ships.sort(key=lambda x: x.ready_date)
            while ships:
                caravan_ships = ships[:self.max_in_caravan]
                ships = ships[self.max_in_caravan:]

                best_caravan = None
                best_quality = float('-inf')

                for icebreaker in port.icebreakers:
                    caravan = Caravan(caravan_ships, icebreaker)
                    if caravan.caravan_quality > best_quality:
                        best_caravan = caravan
                        best_quality = caravan.caravan_quality

                if best_caravan:
                    self.depart_caravan(best_caravan, port)

    def group_ships_by_destination(self, ships: List[Ship]) -> Dict[str, List[Ship]]:
        groups = {}
        for ship in ships:
            if ship.destination not in groups:
                groups[ship.destination] = []
            groups[ship.destination].append(ship)
        return groups

    def depart_caravan(self, caravan: Caravan, port: Port):
        # Update statuses of ships and icebreaker in the caravan
        for ship in caravan.ships:
            port.ships.remove(ship)
            ship.caravan = caravan

        port.icebreakers.remove(caravan.icebreaker)
        caravan.icebreaker.current_port = None

        # Set departure and arrival dates
        caravan.departure_date = max(ship.ready_date for ship in caravan.ships)
        arrival_date = caravan.departure_date + datetime.timedelta(days=calculate_travel_time(None, caravan.icebreaker))
        caravan.icebreaker.available_date = arrival_date
        self.ports[caravan.ships[0].destination].arrival_dates[caravan.icebreaker.icebreaker_id] = arrival_date

        print(f"Caravan with icebreaker {caravan.icebreaker.icebreaker_id} departs from {port.port_name} on {caravan.departure_date} to {caravan.ships[0].destination}.")
