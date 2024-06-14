from PIL import Image, ImageDraw
from matplotlib import pyplot as plt
from mpl_toolkits.basemap import Basemap
import pandas as pd
import ast
from search.mapmask import MapMask
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, date
import json

# Загрузка изображения карты
image_path = 'resultMap/map_image.png'
map_img = Image.open(image_path)
df = pd.read_excel('data/parse_data_with_polygon.xlsx')
map = MapMask(image_path)
img_width, img_height = map_img.size

color_dict = {}
color_reverse  = {}

def get_color(index):
    if index <= 0:
        return "red"
    elif 22 > index >= 21:
        return "#42AAFF"
    elif 21 > index >= 15:
        return "#0000FF"
    else:
        return "#000096"
def draw_poly(row, date):
    coords_lat_lon = ast.literal_eval(row['Polygon'])
    color = get_color(row[date])
    pixel_coords = [map.decoder(coord[0], coord[1]) for coord in coords_lat_lon]
    polygon = plt.Polygon(pixel_coords, facecolor=color, linewidth=0)
    ax.add_patch(polygon)
    
def date_to_unix(day, month, year):
    date_str = f'{year}-{month:02d}-{day:02d} 00:00:00'
    date_time = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    return int(date_time.timestamp())

# Создание фигуры и осей
fig, ax = plt.subplots()

# Показ изображения
ax.imshow(map_img)

map_data = {}

def add_years(d, years):
    try:
        # attempt to add years to the date
        return d.replace(year = d.year + years)
    except ValueError:
        # handle leap year case
        return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))

for indec, date_str in enumerate(df.columns[3:]):
    # Преобразование даты из строки в объект datetime
    date_1 = add_years(datetime.strptime(date_str, '%d-%b-%Y'),2)
    date_2 = add_years(datetime.strptime(df.columns[3+1], '%d-%b-%Y'),2)
    start_time = date_to_unix(date_1.day, date_1.month, date_1.year)
    end_time = date_to_unix(date_2.day, date_2.month, date_2.year)
    print(date_1, date_2)
    fig, ax = plt.subplots()

    # Показ изображения
    ax.imshow(map_img)

    # Применение функции draw_poly к каждой строке DataFrame для текущей недели
    df.apply(lambda x: draw_poly(x, date_str), axis=1)

    ax.set_xlim(0, img_width)
    ax.set_ylim(0, img_height)
    plt.gca().invert_yaxis()
    ax.axis('off')
    fig.set_size_inches(img_width+1208+317, img_height+886+265)

    # Сохранение изображения в отдельный файл для каждой недели
    file_name = f'resultMap/map_ice_{date_str}.png'
    plt.savefig(file_name, dpi=1, bbox_inches='tight', pad_inches=0)
    plt.close()
    print(date_str)
    # Добавление данных в словарь map_data
    map_data[f'{start_time}-{end_time}'] = file_name

# Сохранение данных в JSON файл
with open(r'data/map_data.json', 'w') as json_file:
    json.dump(map_data, json_file, indent=4)

print("JSON файл сохранен как map_data.json")
