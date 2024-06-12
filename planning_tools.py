import datetime
import heapq
from typing import List, Dict, Tuple, Optional
import itertools

class Ship:
    def __init__(self, ship_id: int, destination: str, ready_date: datetime.date, ice_class: int, init_location: str, speed: int):
        self.ship_id = ship_id
        self.init_location = init_location
        self.destination = destination
        self.ready_date = ready_date
        self.ice_class = ice_class
        self.speed = speed
        self.caravan = None

class Icebreaker:
    def __init__(self, icebreaker_id: int, location: str, ice_class: int, speed: float):
        self.icebreaker_id = icebreaker_id
        self.location = location
        self.destination = datetime.date.today()
        self.available_date = None
        self.speed = speed
        self.ice_class = ice_class

class Port:
    def __init__(self, port_name: str):
        self.port_name = port_name
        self.ships = {}
        self.icebreakers = {}
        self.arriving_icebreakers = {}

    def add_ship(self, ship_id: int, ship: Ship):
        self.ships[ship_id] = ship

    def add_icebreaker(self, icebreaker_id: int, icebreaker: Icebreaker):
        self.icebreakers[icebreaker_id] = icebreaker

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


'''
----------------------------------------------------------------------------------------------
Class for storing planned routes, dates and included ships
----------------------------------------------------------------------------------------------
add_route          - add new planned route with all required info about it
get_routes_by_date - return all routes planned for current date (departing/arriving)
'''
class RouteSchedule:
    def __init__(self):
        self.routes = []

    def add_route(self, departure_date: datetime.date, arrival_date: datetime.date, 
                  departure_port: str, arrival_port: str, movement_type: str, participants: List[str]):
        route = {
            'departure_date': departure_date,
            'arrival_date': arrival_date,
            'departure_port': departure_port,
            'arrival_port': arrival_port,
            'movement_type': movement_type,
            'participants': participants
        }
        self.routes.append(route)

    def get_routes_by_date(self, date: datetime.date) -> List[Dict]:
        return [route for route in self.routes if route['departure_date'] == date or route['arrival_date'] == date]

'''
----------------------------------------------------------------------------------------------
Class for whole planning process
----------------------------------------------------------------------------------------------
__init__                    - initialize parameters for system
run_daily_planning          - daily iteration for schedule, planning and ships status update
check_new_applications      - adding application online
check_ice_conditions        - check ice condition changes
optimize_routes             - routes optimization for ships that are already on route (can be triggered by ice chacnges)
plan_shipments              - departure planning with/without icebreaker for each port
plan_caravan_shipment       - if there are icebreakers in port, plan caravan shipment
group_ships_by_destination  - group ships from one port 
find_best_caravan           - find most time-profitable combination of ships to form a caravan with cur icebreaker


'''
class PlanningSystem:
    def __init__(self, ports: List[Port], max_in_caravan: int, max_icebreakers: int, current_date: datetime.date):
        self.ports = {port.port_name: port for port in ports}
        self.max_in_caravan = max_in_caravan
        self.max_icebreakers = max_icebreakers
        self.current_date = current_date
        self.schedule = RouteSchedule()

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
            if port.icebreakers:
                self.plan_caravan_shipment(port)
        
        for port_name, port in self.ports.items():
            self.check_icebreaker_availability(port)
            self.plan_remaining_ships(port)

    def plan_caravan_shipment(self, port: Port):
        # Step 1: Group ships by destination
        destination_groups = self.group_ships_by_destination(port.ships)

        # Step 2: Form caravans for each destination group
        for destination, ships in destination_groups.items():
            best_caravan = self.find_best_caravan(ships, port.icebreakers)

            if best_caravan:
                self.record_caravan_route(best_caravan, port)

    def group_ships_by_destination(self, ships: List[Ship]) -> Dict[str, List[Ship]]:
        groups = {}
        for ship in ships:
            if ship.destination not in groups:
                groups[ship.destination] = []
            groups[ship.destination].append(ship)
        return groups

    def find_best_caravan(self, ships: List[Ship], icebreakers: List[Icebreaker]) -> Tuple[Optional[Caravan], float]:
        best_caravan = None
        best_quality = float('-inf')

        # Generate all possible combinations of ships for sizes from 1 to max_in_caravan
        for size in range(1, self.max_in_caravan + 1):
            for comb in itertools.combinations(ships, size):
                if None in comb:
                    continue
                for icebreaker in icebreakers:
                    caravan = Caravan(list(comb), icebreaker, self.max_in_caravan)
                    if caravan.caravan_quality > best_quality:
                        best_caravan = caravan
                        best_quality = caravan.caravan_quality

        return best_caravan #, best_quality

    def check_icebreaker_availability(self, port: Port):
        for icebreaker in port.icebreakers:
            if icebreaker.available_date <= self.current_date:
                best_port, best_value = None, float('-inf')

                if port.ships:
                    best_caravan = self.find_best_caravan(port.ships, port.icebreakers)
                    best_value = best_caravan.caravan_quality

                for other_port in self.ports.values():
                    if other_port == port:
                        continue
                    best_caravan = self.find_best_caravan(other_port.ships, other_port)
                    if best_caravan:
                        travel_time = self.calculate_icebreaker_travel_time_to_port(icebreaker, other_port)
                        port_value = best_caravan.caravan_quality - travel_time
                        if port_value > best_value:
                            best_port, best_value = other_port, port_value
                if best_port:
                    self.reassign_icebreaker(port, best_port, icebreaker)

    def reassign_icebreaker(self, port: Port, best_port: Port, icebreaker: Icebreaker):
        
        travel_time = self.calculate_icebreaker_travel_time_to_port(port, best_port)
        arrival_date = self.current_date + datetime.timedelta(days=travel_time)
        
        self.record_route(departure_date=self.current_date, 
                          arrival_date=arrival_date, 
                          departure_port=port.port_name,
                          arrival_port_port=best_port.port_name, 
                          movement_type='icebreaker',
                          participants=icebreaker)
    
    def plan_remaining_ships(self, port: Port):
        for ship in port.ships:
            # Check if the ship is part of a second-best caravan
            # ... add logic for second-best caravan check -- if not smth else (???)

            # If not, assign independent departure date
            departure_date = ship.ready_date
            travel_time = calculate_ship_travel_time(ship, None)
            arrival_date = departure_date + datetime.timedelta(days=travel_time)
            
            self.record_route(departure_date=departure_date, 
                          arrival_date=arrival_date, 
                          departure_port=port.port_name,
                          arrival_port_port=ship.destination, 
                          movement_type='ship',
                          participants=ship)
    
    def record_caravan_route(self, caravan: Caravan, port: Port):
        # Set departure and arrival dates
        caravan.departure_date = max(ship.ready_date for ship in caravan.ships)
        travel_time = calculate_caravan_travel_time(caravan)
        arrival_date = caravan.departure_date + datetime.timedelta(days=travel_time)
        caravan.icebreaker.available_date = arrival_date

        participants = [ship for ship in caravan.ships] + [caravan.icebreaker]
        self.record_route(departure_date=caravan.departure_date, 
                          arrival_date=arrival_date, 
                          departure_port=port.port_name,
                          arrival_port_port=caravan.ships[0].destination, 
                          movement_type='caravan',
                          participants=participants)

        #print(f"[LOG] Caravan with icebreaker {caravan.icebreaker.icebreaker_id} departs from {port.port_name} on {caravan.departure_date} to {caravan.ships[0].destination} arriving at {arrival_date}.")
    
    def record_route(self, departure_date: datetime.date, arrival_date: datetime.date, 
                     departure_port: str, arrival_port: str, movement_type: str, 
                     participants: List[str]):
        
        self.schedule.add_route(departure_date, arrival_date, departure_port, arrival_port, movement_type, participants)

    def update_schedule(self):
        routes_today = self.schedule.get_routes_by_date(self.current_date)
        for route in routes_today:
            if route['departure_date'] == self.current_date:
                # Handle departure
                self.handle_departure(route)
            elif route['arrival_date'] == self.current_date:
                # Handle arrival
                self.handle_arrival(route)
            else:
                print(f'WARNING: Can not handle route. Date: {self.current_date}. Route: {route}')

    def handle_departure(self, route: Dict):
        port = self.ports[route['departure_port']]
        destination_port = self.ports[route['arrival_port']]
        if route['movement_type'] == 'caravan':
            icebreaker = None
            for participant_id in route['participants']:
                ship = next((s for s in port.ships if s.ship_id == participant_id), None)
                if ship:
                    port.remove_ship(ship)
                else:
                    icebreaker = next((ib for ib in port.icebreakers if ib.icebreaker_id == participant_id), None)
                    if icebreaker:
                        port.remove_icebreaker(icebreaker)
                        icebreaker.current_port = None
                        destination_port.add_arriving_icebreaker(icebreaker, route['arrival_date'])
        elif route['movement_type'] == 'icebreaker':
            icebreaker = next((ib for ib in port.icebreakers if ib.icebreaker_id == route['participants'][0]), None)
            if icebreaker:
                port.remove_icebreaker(icebreaker)
                icebreaker.current_port = None
                destination_port.add_arriving_icebreaker(icebreaker, route['arrival_date'])
        elif route['movement_type'] == 'ship':
            ship = next((s for s in port.ships if s.ship_id == route['participants'][0]), None)
            if ship:
                port.remove_ship(ship)

    def handle_arrival(self, route: Dict):
        port = self.ports[route['arrival_port']]
        if route['movement_type'] == 'caravan' or route['movement_type'] == 'icebreaker':
            for participant_id in route['participants']:
                icebreaker = next((ib for ib in port.arriving_icebreakers.values() if ib.icebreaker_id == participant_id), None)
                if icebreaker:
                    port.add_icebreaker(icebreaker)
                    port.remove_arriving_icebreaker(icebreaker)
        if route['movement_type'] == 'caravan' or route['movement_type'] == 'ship':
            for participant_id in route['participants']:
                ship = next((s for s in port.ships if s.ship_id == participant_id), None)
                if ship:
                    port.add_ship(ship)

    def calculate_icebreaker_travel_time_to_port(self, from_port: Port, to_port: Port) -> int:
        # Placeholder function to calculate travel time between ports
        return 5  # Example fixed travel time