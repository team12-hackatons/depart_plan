import numpy as np
import pandas as pd
from scipy.spatial import KDTree


class Square:
    def __init__(self, top_left, bottom_right, center_point, index):
        self.top_left = top_left
        self.bottom_right = bottom_right
        self.center = center_point
        self.index = self.get_index(index)
        # self.center = [(top_left[0] + bottom_right[0]) / 2, (top_left[1] + bottom_right[1]) / 2]

    def contains(self, point):
        test01 = self.bottom_right[0] <= point[0] <= self.top_left[0]
        test02 = self.top_left[1] <= point[1] <= self.bottom_right[1]
        return test01 and test02
    @staticmethod
    def get_index(index):
        if index <= 0:
            return 1000
        elif 22 > index >= 21:
            return 1
        elif 21 > index >= 15:
            return 2
        else:
            return 3

class Ice:

    def __init__(self):
        self.df = pd.read_excel('../data/parse_data_ice_tree.xlsx')

        self.squares = []

        for index, row in self.df.iterrows():
            top_left = (row['top_left_lat'], row['top_left_lon'])
            bottom_right = (row['bottom_right_lat'], row['bottom_right_lon'])
            center = (row['center_lat'], row['center_lon'])
            self.squares.append(Square(top_left, bottom_right, center, row['03-Mar-2020']))

     # Построение KD-дерева
        centers = np.array([square.center for square in self.squares])
        self.kd_tree = KDTree(centers)

    def find_nearest_square(self, point, num_neighbors=3):
        # Находим несколько ближайших квадратов
        distances, indices = self.kd_tree.query(point, k=num_neighbors)

        # Проверяем, попадает ли точка в какой-либо из ближайших квадратов
        for idx in indices:
            if self.squares[idx].contains(point):
                return self.squares[idx], True

        # Если ни один из ближайших квадратов не содержит точку, возвращаем ближайший
        nearest_square_index = indices[np.argmin(distances)]
        return self.squares[nearest_square_index], False

    # Пример использования
# point = (69.61121, 48.64746)  # Точка в Москве
# cc = Ice()
# nearest_square, is_inside = cc.find_nearest_square(point)
#
# if is_inside:
#     print(f"Point {point} is inside a square with center at {nearest_square.center}.")
# else:
#     print(f"Point {point} is not inside any square. Nearest square center is at {nearest_square.center}.")

