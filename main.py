import datetime

from planning_tools import Ship, Port, Icebreaker
from planning_tools import PlanningSystem

# Example setup
ports = [Port("PortA"), Port("PortB")]
system = PlanningSystem(ports, max_in_caravan=5, max_icebreakers=4)

# Add some ships and icebreakers for testing
system.ports["PortA"].add_ship(Ship(1, "PortB", datetime.date(2024, 6, 1)))
system.ports["PortA"].add_ship(Ship(2, "PortB", datetime.date(2024, 6, 2)))
system.ports["PortA"].add_icebreaker(Icebreaker(1, "PortA", datetime.date(2024, 6, 1)))

# Run daily planning (this will run indefinitely in this example, you may want to add a termination condition)
system.run_daily_planning()