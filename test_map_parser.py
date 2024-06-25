import folium
import os
import geopandas as gpd
from folium.plugins import MarkerCluster
from mpl_toolkits.basemap import Basemap
from shapely.geometry import Polygon
from geopy.distance import geodesic
import pandas as pd
import ast
from search.mapmask import MapMask

file_path = 'data/parse_data_ice_tree.xlsx'

df = None
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
    #     if normalize_longitude < 0:
    #         return normalize_longitude + 360
    #     return normalize_longitude


    def generate_square(longitude, latitude, side_length):
        # longitude = normalize_longitude(longitude)
        top_right_point = geodesic(kilometers=side_length).destination((latitude, 0), 90)
        bottom_right_point = geodesic(kilometers=side_length).destination(
            (top_right_point.latitude, top_right_point.longitude), 180)
        points = None
        # if longitude > 0 > bottom_right_point.longitude:
        #     points = [
        #         [latitude, longitude],
        #         [bottom_right_point.latitude, 180],
        #     ]
        # else:
        points = [
            [latitude, longitude],
            [bottom_right_point.latitude, bottom_right_point.longitude + longitude],
        ]
        # for point in points:
        #     if not mapMask.is_aqua(point[0], point[1]):
        #         return points, "land"\
        center = [(points[0][0] + points[1][0]) / 2, (points[0][1] + points[1][1]) / 2]

        return points[0], points[1], center
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
            top_left, bottom_right, center = generate_square(lon, lat, side_length_km)
            started_lon = bottom_right[1]
            indices = [top_left[0], top_left[1], bottom_right[0], bottom_right[1], center[0], center[1]]

            for sheet, index_df in index_sheets.items():
                index = float(index_df.iloc[i, j])
                indices.append(index if pd.notna(index) else None)

            # if tag == "aqua":
            data.append(indices)

    columns = ['top_left_lat', 'top_left_lon', 'bottom_right_lat', 'bottom_right_lon', 'center_lat', 'center_lon']

    for sheet in index_sheets.keys():
        columns.append(sheet)

    df = pd.DataFrame(data, columns=columns)

    output_file_path = 'data/parse_data_ice_tree.xlsx'
    df.to_excel(output_file_path, index=False)

    print(df)

# print(df.iloc[0]["Polygon"])
print(df.iloc[0])

