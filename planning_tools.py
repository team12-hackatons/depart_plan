import datetime
import heapq
from typing import List, Dict
import itertools

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
        self.arriving_icebreakers = {}

    def add_ship(self, ship: Ship):
        self.ships.append(ship)

    def add_icebreaker(self, icebreaker: Icebreaker):
        self.icebreakers.append(icebreaker)

    def add_arriving_icebreaker(self, icebreaker: Icebreaker, arriving_date: datetime.date):
        self.arriving_icebreakers[icebreaker.icebreaker_id] = [arriving_date, icebreaker]
    
    def remove_icebreaker(self, icebreaker: Icebreaker):
        self.icebreakers.remove(icebreaker)

    def remove_ship(self, ship: Ship):
        self.ships.remove(ship)
    
    def remove_arriving_icebreaker(self, icebreaker: Icebreaker):
        self.arriving_icebreakers.pop(icebreaker.icebreaker_id)

class Caravan:
    def __init__(self, ships: List[Ship], icebreaker: Icebreaker, max_ships: int):
        if len(ships) > max_ships:
            raise ValueError("too many ships in caravan")
        self.ships = ships
        self.icebreaker = icebreaker
        self.departure_date = max(ship.ready_date for ship in ships)
        self.caravan_quality = self.calculate_caravan_quality()

    def calculate_caravan_quality(self):
        quality = 0
        time_with_icebreaker = calculate_caravan_travel_time(self)
        for ship in self.ships:
            time_alone = calculate_ship_travel_time(ship, None)
            if time_alone == -1:
                time_profit = time_with_icebreaker
            else:
                time_profit = time_alone - time_with_icebreaker
            quality += time_profit
        return quality

def calculate_ship_travel_time(ship: Ship, icebreaker: Icebreaker) -> int:
    # Placeholder for travel time calculation function
    # Calculates ship solo-trip time 
    # returns travel time in days
    pass

def calculate_caravan_travel_time(caravan: Caravan) -> int:
    # Placeholder for travel time calculation function
    # Calculates caravan trip time depending on the weakest ship in group 
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
            self.check_icebreaker_availability(port)

    def plan_port_shipments(self, port: Port):
        # Step 1: Group ships by destination
        destination_groups = self.group_ships_by_destination(port.ships)

        # Step 2: Form caravans for each destination group
        for destination, ships in destination_groups.items():
            best_caravan = None
            best_quality = float('-inf')

            # Generate all possible combinations of ships for sizes from 1 to max_in_caravan
            for size in range(1, self.max_in_caravan + 1):
                for comb in itertools.combinations(ships, size):
                    for icebreaker in port.icebreakers:
                        caravan = Caravan(list(comb), icebreaker, self.max_in_caravan)
                        if caravan.caravan_quality > best_quality:
                            best_caravan = caravan
                            best_quality = caravan.caravan_quality

            if best_caravan and len(port.icebreakers) > 0:
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
        arrival_date = caravan.departure_date + datetime.timedelta(days=calculate_caravan_travel_time(caravan))
        caravan.icebreaker.available_date = arrival_date
        self.ports[caravan.ships[0].destination].add_arriving_icebreaker(caravan.icebreaker, arrival_date)

        print(f"[LOG] Caravan with icebreaker {caravan.icebreaker.icebreaker_id} departs from {port.port_name} on {caravan.departure_date} to {caravan.ships[0].destination} arriving at {arrival_date}.")


    def check_icebreaker_availability(self, port: Port):
        if port.icebreakers:
            self.reassign_icebreaker(port)

    def calculate_icebreaker_travel_time_to_port(self, from_port: Port, to_port: Port) -> int:
        # Placeholder function to calculate travel time between ports
        return 5  # Example fixed travel time

    def reassign_icebreaker(self, port: Port):
        best_port = None
        best_value = float('-inf')

        for other_port in self.ports.values():
            if other_port == port:
                continue
            best_caravan_quality = float('-inf')
            for destination, ships in self.group_ships_by_destination(other_port.ships).items():
                for size in range(1, self.max_in_caravan + 1):
                    for comb in itertools.combinations(ships, size):
                        caravan = Caravan(list(comb), None, self.max_in_caravan)
                        if caravan.caravan_quality > best_caravan_quality:
                            best_caravan_quality = caravan.caravan_quality
            travel_time = self.calculate_icebreaker_travel_time_to_port(port, other_port)
            port_value = best_caravan_quality - travel_time
            if port_value > best_value:
                best_value = port_value
                best_port = other_port

        if best_port:
            # Assign an icebreaker to the best port
            best_caravan = max(best_port.icebreakers, key=lambda x: x.available_date)
            port.add_icebreaker(best_caravan)
            best_port.remove_icebreaker(best_caravan)
            travel_time = self.calculate_icebreaker_travel_time_to_port(port, best_port)
            arrival_date = self.current_date + datetime.timedelta(days=travel_time)
            port.add_arriving_icebreaker(best_caravan, arrival_date)

