import datetime
import pandas as pd
from planning_tools import Ship, Port, Icebreaker, calculate_ship_travel_time
from planning_tools import PlanningSystem, Caravan
from datetime import datetime


graph_df  = pd.read_excel(r'data\ГрафДанные.xlsx', sheet_name='points')
graph_df.drop(columns=['Unnamed: 5','Unnamed: 6'], inplace=True)

ships_df = pd.read_excel(r'data\timetable.xlsx', sheet_name='Sheep')
icebracker_df = pd.read_excel(r'data\timetable.xlsx', sheet_name='Icebracer')

def generate_ship(ship_row):
    return Ship(
    ship_id=ship_row.name, destination=ship_row['Пункт окончания плавания'].upper(), ready_date=ship_row['Дата начала плавания'],
    ice_class=ship_row['Ледовый класс'], init_location=ship_row['Пункт начала плавания'].upper(),
    speed=ship_row['Скорость, узлы\n(по чистой воде)'], ship_name=ship_row['Название судна'].upper()
    )

def generate_icebracker(df_row): 
    return Icebreaker(
    icebreaker_id=df_row.name, location=df_row['Начальное положение ледоколов на 27 февраля 2022'].upper(),
    ice_class=df_row['Ледовый класс'], speed=df_row['Скорость, узлы \n(по чистой воде)'], icebreaker_name= df_row['Наименование']
    )


# Example setup
ports = {port_name.upper():Port(port_name.upper()) for port_name in graph_df['point_name']}
ships = {ind: val for ind, val in enumerate(ships_df.apply(lambda row: generate_ship(row), axis=1))}
icebreakers = {ind: val for  ind, val in enumerate(icebracker_df.apply(lambda row: generate_icebracker(row), axis=1))}


print(ships.items())

test_ship_num = 5 # only for test
for k,v in ships.items():
    ports[v.init_location].add_ship(v)
    
    # only for test
    test_ship_num -= 1
    if test_ship_num == 0:
        break

test_icebreaker_num = 2   
for k,v in icebreakers.items():
    ports[v.location].add_icebreaker(v)

    # only for test
    test_icebreaker_num -= 1
    if test_icebreaker_num == 0:
        break
#for snip in list(ships.values()): print(calculate_ship_travel_time(snip))
plan = PlanningSystem(ports.values(), max_icebreakers=4, max_in_caravan=3,current_date= min([ship_1.ready_date for ship_1 in ships.values()]))
plan.run_daily_planning()
plan.schedule.print_schedule()
plan.schedule.save_schedule_json()