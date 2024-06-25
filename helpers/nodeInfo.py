from datetime import datetime

from geopy.distance import geodesic
from search.testMapMask import MapMask

class NodeInfo:
    end_lat = None
    end_lon = None
     # = None
    start_time = None
    def __init__(self, lat, lon, time_in_path, current_time,  x=None, y=None):
        # if x is None and y is None:
            # x, y = map_mask.decoder(lat, lon)
        # self.map_mask = map_mask
        self.lat = lat
        self.lon = lon
        self.x = x
        self.y = y
        # self.ice_index = self.map_mask.get_ice_index(x, y)
        self.time_in_path = time_in_path
        self.current_time = current_time
        self.distance_to_end = geodesic((lat, lon), (NodeInfo.end_lat, NodeInfo.end_lon)).kilometers

    def set_time(self, time_in_path):
        self.time_in_path = time_in_path

    @classmethod
    def from_xy(cls, x, y, time_in_path, map_mask, current_time):
        if x > map_mask.map_width:
            x = x - map_mask.map_width
        if y < 0:
            y = y + map_mask.map_height
        lat, lon = map_mask.reverse_decoder(x, y)
        return cls(lat, lon, time_in_path, map_mask, current_time, x, y)

    @classmethod
    def set_class(cls, lat, lon, start_time):
        seconds_since_epoch = start_time
        cls.start_time = seconds_since_epoch
        # cls.map_mask = map_mask
        cls.end_lat = lat
        cls.end_lon = lon

# NodeInfo.set_class(64, 34, MapMask('../resultMap/map_image.png'))
# ll = NodeInfo.from_xy(5252, 3000, 0)