import ast
import pandas as pd
from PIL import Image
from matplotlib import pyplot as plt
from matplotlib.patches import Polygon
from search.mapmask import MapMask

# Загрузка изображения карты
image_path = '../resultMap/map_image.png'
map_img = Image.open(image_path)
df = pd.read_excel('../data/parse_data_with_polygon.xlsx')
map_mask = MapMask(image_path)
img_width, img_height = map_img.size

def get_color(index):
    if index <= 0:
        return "red"
    elif 22 > index >= 21:
        return "#42AAFF"
    elif 21 > index >= 15:
        return "#0000FF"
    else:
        return "#000096"

def draw_poly(ax, row, date):
    coords_lat_lon = ast.literal_eval(row['Polygon'])
    color = get_color(row[date])
    pixel_coords = [map_mask.decoder(coord[0], coord[1]) for coord in coords_lat_lon]
    polygon = Polygon(pixel_coords, facecolor=color, edgecolor='none')
    ax.add_patch(polygon)

# Создание фигуры и осей
fig, ax = plt.subplots(figsize=(img_width/1000, img_height/1000))
ax.imshow(map_img)

# Добавление полигонов на изображение
for index, row in df.iterrows():
    draw_poly(ax, row, 'date_column')  # Замените 'date_column' на имя столбца с датами в вашем датафрейме

# Удаление осей и сохранение изображения
ax.axis('off')
plt.savefig('myfig.png', dpi=1000, bbox_inches='tight', pad_inches=0)
plt.show()
