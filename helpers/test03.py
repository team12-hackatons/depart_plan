from shapely.geometry import Polygon, Point
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

# Заданные координаты (широта и долгота) четырёх точек многоугольника
coordinates = [[64.5555, 22.085995576630605], [64.55457885655419, 22.607273307794465], [64.33033173412167, 22.607273307794465], [64.33125290590183, 22.085995576630605]]

# Создание многоугольника
polygon = Polygon(coordinates)

# Функция для проверки, находится ли точка внутри многоугольника, и возврата индекса льда
def get_ice_index(lat, lon, ice_index):
    point = Point(lon, lat)
    if polygon.contains(point):
        return ice_index
    else:
        return None

# Пример координат точки, которую нужно проверить
lat_check, lon_check = 60.0, 30.0

# Индекс льда для заданного многоугольника
ice_index = 1.5  # Например

# Проверка точки и вывод результата
result = get_ice_index(lat_check, lon_check, ice_index)
print(f'Ice Index: {result}')

# Визуализация области и точки
fig, ax = plt.subplots()
m = Basemap(projection='mill', llcrnrlat=-90, urcrnrlat=90, llcrnrlon=-180, urcrnrlon=180)

m.drawcoastlines()
m.drawcountries()

# Преобразование координат для Basemap
x, y = zip(*[m(lon, lat) for lon, lat in coordinates])
m.plot(x + (x[0],), y + (y[0],), marker=None, color='m')

# Добавление точки
xpt, ypt = m(lon_check, lat_check)
m.plot(xpt, ypt, 'bo')

plt.title('Ice Index Area and Point Check')
plt.show()
