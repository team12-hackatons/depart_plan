import datetime
import pandas as pd
from planning_tools import Ship, Port, Icebreaker
from planning_tools import PlanningSystem

graph_df  = pd.read_excel(r'data\ГрафДанные.xlsx', sheet_name='points')
graph_df.drop(columns=['Unnamed: 5','Unnamed: 6'], inplace=True)

ships_df = pd.read_excel(r'data\timetable.xlsx', sheet_name='Sheep')
icebracker_df = pd.read_excel(r'data\timetable.xlsx', sheet_name='Icebracer')

def generate_ship(sheep_row):
    return Ship(
    ship_id=sheep_row.name, destination=sheep_row['Пункт окончания плавания'].upper(), ready_date=sheep_row['Дата начала плавания'],
    ice_class=sheep_row['Ледовый класс'], init_location=sheep_row['Пункт начала плавания'].upper(), speed=sheep_row['Скорость, узлы\n(по чистой воде)']
    )

def generate_icebracker(df_row): 
    return Icebreaker(
    icebreaker_id=df_row.name, location=df_row['Начальное положение ледоколов на 27 февраля 2022'].upper(),
    ice_class=df_row['Ледовый класс'], speed=df_row['Скорость, узлы \n(по чистой воде)']
    )


# Example setup
ports = {port_name.upper():Port(port_name.upper()) for port_name in graph_df['point_name']}
sheeps = {ind: val for ind, val in enumerate(ships_df.apply(lambda row: generate_ship(row), axis=1))}
icebreakers = {ind: val for  ind, val in enumerate(icebracker_df.apply(lambda row: generate_icebracker(row), axis=1))}


for k,v in sheeps.items():
    ports[v.init_location].add_ship(k,v)
    
for k,v in icebreakers.items():
    ports[v.location].add_icebreaker(k,v)
    
print(ports['РЕЙД МУРМАНСКА'].ships, ports['РЕЙД МУРМАНСКА'].icebreakers)

