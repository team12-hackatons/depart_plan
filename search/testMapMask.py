import os
from datetime import datetime
import re
import json
from PIL import Image, ImageDraw
from matplotlib import pyplot as plt
from mpl_toolkits.basemap import Basemap


class MapMask:

    def __init__(self, image_path=r'resultMap/map_image.png'):
        self.ice_map = None
        self.map = Basemap(projection='mill', llcrnrlat=-90, urcrnrlat=90, llcrnrlon=-180, urcrnrlon=180)
        self.image = Image.open(image_path)
        self.last_ice_info = None
        self.map_width, self.map_height = self.image.size

    def change_ice_map(self, current_time, json_path=r'data/map_data.json'):
        # Функция для преобразования даты в Unix время

        
        # Чтение JSON файла
        with open(json_path, 'r') as file:
            data = json.load(file)
        
        # Поиск подходящего диапазона времени
        for time_range, file_path in data.items():
            start_time, end_time = map(int, time_range.split('-'))
            if start_time <= current_time < end_time:
                self.ice_map = Image.open(file_path)
                print('Карта обновилась')
        if current_time< int(min(data.keys(), key=lambda x:  int(x.split('-')[0])).split('-')[0]): 
            self.ice_map =  Image.open(data["1646254800-1646859600"])
        elif current_time> int(max(data.keys(), key=lambda x:  int(x.split('-')[1])).split('-')[0]):
            self.ice_map =  Image.open(data["1653512400-1646859600"])
            

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
        pixel_color = self.ice_map.getpixel((x, y))
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

    def is_aqua(self, x, y):
        pixel_color = self.image.getpixel((x, y))
        # if pixel_color == (255, 0, 0, 255):
        #     return False
        min_x = max(0, x - 2)
        max_x = min(self.map_width - 1, x + 2)
        min_y = max(0, y - 2)
        max_y = min(self.map_height - 1, y + 2)

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
        image_with_point = self.ice_map.copy()  # Создаем копию исходного изображения
        draw = ImageDraw.Draw(image_with_point)
        draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill='green')  # Рисуем точку
        image_with_point.show()

    def plot_point_X_Y(self, points):
        image_with_point = self.image.copy()  # Создаем копию исходного изображения
        draw = ImageDraw.Draw(image_with_point)
        for i in range(len(points)):
            draw.point(points[i], fill='green')
            # draw.ellipse((points[i][0] - 0, points[i][1] - 0, points[i][0] + 0, points[i][1] + 0), fill='green')  # Рисуем точку
        image_with_point.show()
