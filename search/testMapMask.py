import os
from datetime import datetime
import re

from PIL import Image, ImageDraw
from matplotlib import pyplot as plt
from mpl_toolkits.basemap import Basemap


class MapMask:

    def __init__(self, image_path=r'resultMap/map_ice.png'):
        # self.ice_map = None
        self.map = Basemap(projection='mill', llcrnrlat=-90, urcrnrlat=90, llcrnrlon=-180, urcrnrlon=180)
        self.image = Image.open(image_path)
        # self.ice_map = Image.open(ice_map)
        self.map_width, self.map_height = self.image.size

    # def change_ice_map(self, current_time, file_path=r'../resultMap'):
    #     files = os.listdir(file_path)
    #
    #     pattern = re.compile(r'map_ice_(\d{2})-(\w{3})-(\d{4})\.png')
    #
    #     # Месяцы для преобразования из названий в номера
    #     months = {
    #         "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
    #         "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
    #     }

        # def date_to_unix(day, month, year):
        #     date_str = f'{year}-{months[month]}-{day} 00:00:00'
        #     date_time = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        #     return int(date_time.timestamp())

        latest_file = None
        latest_time = 0

        # for file in files:
        #     match = pattern.match(file)
        #     if match:
        #         day, month, year = match.groups()
        #         file_time = date_to_unix(day, month, year)
        #
        #         if current_time >= file_time > latest_time:
        #             latest_time = file_time
        #             latest_file = file
        #
        # if latest_file:
        #     file_path = os.path.join(file_path, latest_file)
        #     self.ice_map = Image.open(file_path)
            # print(f"Изображение {latest_file} было обновлено.")

    def decoder(self, lat, lon):
        x, y = self.map(lon, lat)
        x = int((x - self.map.xmin) / (self.map.xmax - self.map.xmin) * self.map_width)
        y = int((self.map.ymax - y) / (self.map.ymax - self.map.ymin) * self.map_height)
        return x, y

    def reverse_decoder(self, map_x, map_y):
        x = map_x / self.map_width * (self.map.xmax - self.map.xmin) + self.map.xmin
        y = self.map.ymax - map_y / self.map_height * (self.map.ymax - self.map.ymin)

        lon, lat = self.map(x, y, inverse=True)

        return lat, lon

    def get_ice_index(self, x, y):
        pixel_color = self.image.getpixel((x, y))
        if pixel_color == (255, 0, 0, 255):
            return 1000
        elif pixel_color == (0, 0, 150, 255):
            return 3
        elif pixel_color == (0, 0, 255, 255):
            return 2
        elif pixel_color == (66, 170, 255, 255):
            return 1
        else:
            return 0

    def is_aqua(self, x, y, rad = 1):
        x = int(x)
        y = int(y)
        cc = self.image.size
        if(x > cc[0] or x < 0):
            x = cc[0]-1
        if (y > cc[1] or y < 0):
            y = cc[1] - 1
        pixel_color = self.image.getpixel((x, y))
        # if pixel_color == (255, 0, 0, 255):
        #     return False
        # rad = 1
        min_x = max(0, x - rad)
        max_x = min(self.map_width - rad, x + rad)
        min_y = max(0, y - rad)
        max_y = min(self.map_height - rad, y + rad)

        for i in range(min_x, max_x + 1):
            for j in range(min_y, max_y + 1):
                pixel_color = self.image.getpixel((i, j))
                if pixel_color == (255, 255, 255, 255):  # Белый цвет
                    return False
        return True

    def plot_graph_on_map(self, points):
        plt.imshow(self.image)
        for i in range(len(points) - 1):
            x1, y1 = self.decoder(points[i][0], points[i][1])
            x2, y2 = self.decoder(points[i + 1][0], points[i + 1][1])
            # x1, y1 = points[i]
            # x2, y2 = points[i + 1]
            plt.plot([x1, x2], [y1, y2], color='g', linewidth=2)
        plt.show()

    def plot_graph_on_map_X_Y(self, x_cords, y_cords):
        plt.imshow(self.image)
        for i in range(len(x_cords) - 1):
            x1, y1 = x_cords[i], y_cords[i]
            x2, y2 = x_cords[i + 1], y_cords[i + 1]
            # x1, y1 = points[i]
            # x2, y2 = points[i + 1]
            plt.plot([x1, x2], [y1, y2], color='g', linewidth=2)
        plt.show()

    def plot_point(self, lat, lon):
        x, y = self.decoder(lat, lon)
        image_with_point = self.image.copy()  # Создаем копию исходного изображения
        draw = ImageDraw.Draw(image_with_point)
        draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill='red')  # Рисуем точку
        image_with_point.show()

    def plot_point_X_Y(self, points):
        image_with_point = self.image.copy()  # Создаем копию исходного изображения
        draw = ImageDraw.Draw(image_with_point)
        for i in range(len(points)):
            draw.point(points[i], fill='green')
            # draw.ellipse((points[i][0] - 0, points[i][1] - 0, points[i][0] + 0, points[i][1] + 0), fill='green')  # Рисуем точку
        image_with_point.show()
