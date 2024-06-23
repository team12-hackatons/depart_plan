import numpy as np
from scipy.spatial import KDTree

class Square:
    def __init__(self, top_left, bottom_right):
        self.top_left = top_left
        self.bottom_right = bottom_right
        self.center = [(top_left[0] + bottom_right[0]) / 2, (top_left[1] + bottom_right[1]) / 2]

    def contains(self, point):
        test01 =self.bottom_right[0] <= point[0] <= self.top_left[0]
        test02 = self.top_left[1] <= point[1]
        test03 = point[1] <= self.bottom_right[1]
        return ( test01 and test02)

# Пример данных квадратов с реальными координатами широты и долготы
squares = [
    Square((55.7558, 37.6076), (55.7458, 37.6176)),  # Москва
    Square((48.8566, 2.3522), (48.8466, 2.3422)),    # Париж
    Square((40.7128, -74.0060), (40.7028, -73.9960)),# Нью-Йорк
    Square((35.6895, 139.6917), (35.6795, 139.6817)),# Токио
    Square((34.0522, -118.2437), (34.0422, -118.2337))# Лос-Анджелес
]

# Построение KD-дерева
centers = np.array([square.center for square in squares])
kd_tree = KDTree(centers)

def find_nearest_square(point, squares, kd_tree, num_neighbors=3):
    # Находим несколько ближайших квадратов
    distances, indices = kd_tree.query(point, k=num_neighbors)

    # Проверяем, попадает ли точка в какой-либо из ближайших квадратов
    for idx in indices:
        if squares[idx].contains(point):
            return squares[idx], True

    # Если ни один из ближайших квадратов не содержит точку, возвращаем ближайший
    nearest_square_index = indices[np.argmin(distances)]
    return squares[nearest_square_index], False

# Пример использования
point = (55.7500, 37.6100)  # Точка в Москве
nearest_square, is_inside = find_nearest_square(point, squares, kd_tree)

if is_inside:
    print(f"Point {point} is inside a square with center at {nearest_square.center}.")
else:
    print(f"Point {point} is not inside any square. Nearest square center is at {nearest_square.center}.")
