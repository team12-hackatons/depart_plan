import math

import numpy as np
import pandas as pd
from scipy.spatial import KDTree
from geopy.distance import great_circle


class Rads:

    rad = 3
    def __init__(self,  center_point, time):
        self.center = center_point
        self.time = time

    def contains(self, point, time):
        # if self.time > time:
        return self.distance(self.center, point) <= self.rad
        # return False

    @staticmethod
    def distance(point1, point2):
        return great_circle(point1, point2).kilometers


class VisitedRads:
    def __init__(self):
        self.rads = []
        self.kd_tree = KDTree(np.empty((0, 2)))
        # centers = np.array([square.center for square in squares])


    def find_nearest_rad(self, point, time, num_neighbors=3):
        distances, indices = self.kd_tree.query(point, k=num_neighbors)

        for idx in indices:
            if idx < len(self.rads):
                if self.rads[idx].contains(point, time):
                    return self.rads[idx]
            else:
                break
        return False

    def add_rads(self, center_point, time):
        new_rad = Rads(center_point, time)
        self.rads.append(new_rad)

        # Обновляем KD-дерево с новыми центрами
        centers = np.array([rad.center for rad in self.rads])
        self.kd_tree = KDTree(centers)

# point = (69.61121, 48.64746)  # Точка в Москве
# vis = VisitedRads()
# vis.add_rads( point, 10)
# cc = vis.find_nearest_rad(point,5)
# cc.time = 5
# vis.add_rads(point, 5)
# print(cc)
# nearest_square, is_inside = find_nearest_square(point, squares, kd_tree)

# if is_inside:
#     print(f"Point {point} is inside a square with center at {nearest_square.center}.")
# else:
#     print(f"Point {point} is not inside any square. Nearest square center is at {nearest_square.center}.")

