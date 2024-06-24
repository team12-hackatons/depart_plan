import folium
import os
import geopandas as gpd
from folium.plugins import MarkerCluster
from shapely.geometry import Polygon
from geopy.distance import geodesic
import pandas as pd
import ast
from search.mapmask import MapMask

file_path = 'data/parse_data_with_polygon.xlsx'

df = None
max_lon = [0]
if False:
    df = pd.read_excel(file_path)

    print(df)
else:
    file_path_integr_velocity = 'data/IntegrVelocity.xlsx'

    sheets = pd.ExcelFile(file_path_integr_velocity).sheet_names

    lon_df = pd.read_excel(file_path_integr_velocity, sheet_name='lon')
    lat_df = pd.read_excel(file_path_integr_velocity, sheet_name='lat')

    index_sheets = {sheet: pd.read_excel(file_path_integr_velocity, sheet_name=sheet) for sheet in sheets if
                    sheet not in ['lon', 'lat']}

    data = []

    side_length_km = 25


    # def normalize_longitude(normalize_longitude):
    #     if normalize_longitude > 180:
    #         return normalize_longitude - 360
    #     return normalize_longitude
    #
    #
    def nor(lon):
        # div = lon % 180
        # if div % 2 == 0:
        #     return (lon // (180 * div)) + 20
        # else:
        #     return 200 - (lon // (180 * div))
        return lon
    def generate_square(longitude, latitude, side_length, i):
        # longitude = normalize_longitude(longitude)
        top_right_point = geodesic(kilometers=side_length).destination((latitude, 0), 90)
        bottom_right_point = geodesic(kilometers=side_length).destination(
            (top_right_point.latitude, top_right_point.longitude), 180)
        bottom_left_point = geodesic(kilometers=side_length).destination((latitude, 0), 180)
        points = None
        # if longitude <= 200:
        # if i >= 32164:
        #     print(longitude)
        points = [
            [latitude, nor(longitude)],
            [top_right_point.latitude, nor(top_right_point.longitude + longitude)],
            [bottom_right_point.latitude, nor(bottom_right_point.longitude + longitude)],
            [bottom_left_point.latitude, nor(bottom_left_point.longitude + longitude)]
        ]
        # if longitude > 200:
        #     # longitude
        #     points = [
        #         [top_right_point.latitude, longitude - top_right_point.longitude],
        #         [latitude, longitude],
        #         [bottom_left_point.latitude, longitude - bottom_left_point.longitude],
        #         [bottom_right_point.latitude, longitude - bottom_right_point.longitude],
        #     ]
        # for point in points:
        #     if not mapMask.is_aqua(point[0], point[1]):
        #         return points, "land"
        return points, "aqua"
        # bottom_left = list(geodesic(kilometers=side_length).destination((latitude, longitude), 225))[:2]
        # bottom_right = list(geodesic(kilometers=side_length).destination((latitude, longitude), 315))[:2]
        # top_right = list(geodesic(kilometers=side_length).destination((latitude, longitude), 45))[:2]
        # top_left = list(geodesic(kilometers=side_length).destination((latitude, longitude), 135))[:2]

        # square_polygon = [bottom_left, bottom_right, top_right, top_left]
        #
        # return square_polygon

    # map = MapMask()
    for i in range(len(lon_df)):
        started_lon = None
        for j in range(lon_df.shape[1]):
            lon = lon_df.iloc[i, j]
            lat = lat_df.iloc[i, j]
            # if started_lon is None:
            #     started_lon = lon
            # elif started_lon <= lon:
            #     started_lon = lon
            # else:
            #     lon = started_lon

            square, tag = generate_square(lon, lat, side_length_km, i*j)
            started_lon = square[1][1]
            indices = [square, lon, lat]

            for sheet, index_df in index_sheets.items():
                index = float(index_df.iloc[i, j])
                indices.append(index if pd.notna(index) else None)

            if tag == "aqua":
                data.append(indices)

    columns = ['Polygon', 'Longitude', 'Latitude']
    for sheet in index_sheets.keys():
        columns.append(sheet)

    df = pd.DataFrame(data, columns=columns)

    output_file_path = 'data/parse_data_with_polygon.xlsx'
    df.to_excel(output_file_path, index=False)

    print(df)

print(df.iloc[32164]["Polygon"])
print(df.iloc[32164])
print(max_lon)

m = folium.Map(location=[70.0, -30.0], zoom_start=2)


def get_color(index):
    if index <= 0:
        return "red"
    elif 22 > index >= 21:
        return "#42AAFF"
    elif 21 > index >= 15:
        return "#0000FF"
    else:
        return "#000096"


def add_ice_area(map_object, polygon_info, get_ice_index_from, index):
    folium.Polygon(
        locations=polygon_info["Polygon"],
        color=get_color(polygon_info[get_ice_index_from]),
        fill=True,
        fill_color=get_color(polygon_info[get_ice_index_from]),
        fill_opacity=0.5,
        tooltip=str(index)
    ).add_to(map_object)


# current_cluster = MarkerCluster().add_to(m)
#
# folium.Polygon(
#     locations=ast.literal_eval(polygon_info["Polygon"]),
#     color=get_color(-20),
#     fill=True,
#     fill_color=get_color(-20),
#     fill_opacity=0.5,
#     # tooltip=str(index)
# ).add_to(current_cluster)

for index, polygon_data in df.iterrows():
    # Каждые 100 полигонов создаем новый кластер
    if index % 100 == 0:
        current_cluster = MarkerCluster().add_to(m)

    add_ice_area(current_cluster, polygon_data, "03-Mar-2020", index)
    # break
    # if index >= 30000:
    #     break

m.save('ice_map.html')
