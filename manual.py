import matplotlib
import shapely
from shapely import GeometryCollection, box, MultiPolygon, LineString
from shapely.geometry import Polygon, Point
import re
import random
import geopandas as gpd
import matplotlib.pyplot as plt


matplotlib.use('Qt5Agg')
plt.ion()
fig, ax = plt.subplots()
plt.show()

def to_multi(p, as_list=False):
    ext_s = []
    if isinstance(p, Polygon):
        ext_s = [p]
    elif isinstance(p, MultiPolygon):
        ext_s = [pp.buffer(0) for pp in list(p.geoms)]
    elif isinstance(p, GeometryCollection):
        for pp in list(p.geoms):
            if isinstance(pp, MultiPolygon):
                ext_s = [pp.buffer(0) for pp in list(p.geoms)]
            else:
                ext_s = [p.buffer(0)]
    elif isinstance(p, LineString):
        ext_s = [p.buffer(0)]

    elif isinstance(p, (tuple, list)):
        ext_s = sum([to_multi(pp, as_list=True) for pp in p], [])
    else:
        ext_s = [pp.buffer(0) for pp in list(p)]

    if as_list:
        return ext_s
    return MultiPolygon(ext_s).buffer(0)


def exterior(poly, w=2):
    if isinstance(poly, Polygon):
        return poly.exterior.buffer(w, join_style=2, cap_style=2)
    elif isinstance(poly, MultiPolygon):
        return MultiPolygon([p.exterior.buffer(w, join_style=2, cap_style=2) for p in poly.geoms])
    elif isinstance(poly, GeometryCollection):
        return GeometryCollection([p.exterior.buffer(w, join_style=2, cap_style=2) for p in poly.geoms])
    elif isinstance(poly, LineString):
        return poly.buffer(w, join_style=2, cap_style=2)
    elif isinstance(poly, (tuple, list)):
        ext_s = [exterior(p) for p in poly]
        return to_multi(ext_s)


def get_box(centroid, width, height):
    x, y = centroid.coords[0]
    return box(x - width / 2, y - height / 2, x + width / 2, y + height / 2)


def parse_points(input_str):
    # Extract the coordinate pairs using regex
    coords_str = re.findall(r'\((\d+)\s(\d+)\)', input_str)

    # Convert coordinate pairs to Shapely Points and store them in a list
    points = [Point(int(x), int(y)) for x, y in coords_str]

    return points


room_centroids = parse_points("[<POINT (186 106)>, <POINT (201 147)>, <POINT (60 148)>]")
bathroom_centroids = parse_points("[<POINT (159 156)>, <POINT (147 98)>, <POINT (220 120)>]")

no_rooms = len(room_centroids)
no_bathrooms = len(bathroom_centroids)

door_poly = shapely.from_wkt("POLYGON ((25.60000000000004 83.94534091435006, 25.60000000000004 104.88910346265587, "
                             "30.835940637076458 104.88910346265587, 30.835940637076458 102.87003020908385, "
                             "28.21797031853825 102.87003020908385, 28.21797031853825 83.94534091435006, "
                             "25.60000000000004 83.94534091435006))")
inner_poly = shapely.from_wkt("POLYGON ((28.21797031853825 83.45141718883046, 213.26592968801174 83.45141718883046, "
                              "213.26592968801174 107.43911562561406, 230.39999999999995 107.43911562561406, "
                              "230.39999999999995 172.54858281116952, 32.78705573506845 172.54858281116952, "
                              "32.78705573506845 129.14227135413256, 38.49841250573122 129.14227135413256, "
                              "38.49841250573122 102.87003020908385, 28.21797031853825 102.87003020908385, "
                              "28.21797031853825 83.45141718883046))")



room_centroids = parse_points("[<POINT (81 105)>, <POINT (55 151)>, <POINT (134 105)>]")
bathroom_centroids = parse_points("[<POINT (40 115)>, <POINT (101 160)>]")

no_rooms = len(room_centroids)
no_bathrooms = len(bathroom_centroids)

door_poly = shapely.from_wkt(
    "POLYGON ((230.4 176.09107942600446, 230.4 154.0103857791844, 227.63991329414748 154.0103857791844, 227.63991329414748 176.09107942600446, 230.4 176.09107942600446))")
inner_poly = shapely.from_wkt(
    "POLYGON ((105.44810944559121 78.39738655652667, 198.6042371321142 78.39738655652667, 198.6042371321142 91.70540479745854, 227.63991329414748 91.70540479745854, 227.63991329414748 177.60261344347333, 25.599999999999994 177.60261344347333, 25.599999999999994 101.38396351813626, 52.21603648186374 101.38396351813626, 52.21603648186374 78.39738655652667, 105.44810944559121 78.39738655652667))")


#
# room_centroids = parse_points("[<POINT (192 164)>, <POINT (190 107)>, <POINT (60 165)>]")
# bathroom_centroids = parse_points("[<POINT (145 98)>, <POINT (146 172)>, <POINT (107 175)>]")
#
# no_rooms = len(room_centroids)
# no_bathrooms = len(bathroom_centroids)
#
# door_poly = shapely.from_wkt(
#     "POLYGON ((52.786267475558176 62.04555182296029, 27.721157248983484 62.04555182296029, 27.721157248983484 65.17869060128213, 52.786267475558176 65.17869060128213, 52.786267475558176 62.04555182296029))")
# inner_poly = shapely.from_wkt(
#     "POLYGON ((25.599999999999994 65.17869060128213, 53.527272727272745 65.17869060128213, 53.527272727272745 71.38475120734273, 135.7575757575758 71.38475120734273, 135.7575757575758 79.14232696491848, 230.4 79.14232696491848, 230.4 193.9544481770397, 25.599999999999994 193.9544481770397, 25.599999999999994 65.17869060128213))")
#


# room_centroids = parse_points("[<POINT (192 119)>, <POINT (120 106)>]")
# bathroom_centroids = parse_points("[<POINT (208 163)>, <POINT (91 100)>]")
#
# no_rooms = len(room_centroids)
# no_bathrooms = len(bathroom_centroids)
#
# door_poly = shapely.from_wkt("POLYGON ((25.599999999999948 133.94369064624638, 25.599999999999948 154.6958571747822, 28.194020816066946 154.6958571747822, 28.194020816066946 133.94369064624638, 25.599999999999948 133.94369064624638))")
# inner_poly = shapely.from_wkt("POLYGON ((80.7357319426007 77.84654847012683, 157.16003903574074 77.84654847012683, 157.16003903574074 87.39958685676936, 230.4 87.39958685676936, 230.4 178.15345152987317, 28.194020816066946 178.15345152987317, 28.194020816066946 130.38825959666062, 80.7357319426007 130.38825959666062, 80.7357319426007 77.84654847012683))")


random.shuffle(room_centroids)
random.shuffle(bathroom_centroids)

alle = gpd.GeoSeries([inner_poly,
                      door_poly,
                      inner_poly,
                      GeometryCollection(room_centroids),
                      GeometryCollection(bathroom_centroids)])
# alle.plot(cmap="Dark2")

# plt.show()

import time


class Room:
    def __init__(self, center=None, width=1, height=1):
        self.width = width
        self.height = height
        self.centroid = center
        self.poly = get_box(self.centroid, self.width, self.height)
        self.area = 0
        self.max_dim = 0

    def increase_width(self, amount=0.1):
        self.width += amount
        self.poly = get_box(self.centroid, self.width, self.height)
        self.area = self.poly.area
        self._update_max_dim()

    def increase_height(self, amount=0.1):
        self.height += amount
        self.poly = get_box(self.centroid, self.width, self.height)
        self.area = self.poly.area
        self._update_max_dim()

    def horiz_intersection(self, boundary_exterior, w=1):
        x1, y1, x2, y2 = self.poly.exterior.bounds
        horiz_lines = [shapely.geometry.LineString([(x1, y1), (x2, y1)]),
                       shapely.geometry.LineString([(x1, y2), (x2, y2)])]

        horizontal_shapes = [exterior(line, w) for line in horiz_lines]
        inter = [shape.intersection(boundary_exterior) for shape in horizontal_shapes]
        return to_multi(inter)

    def vert_intersection(self, boundary_exterior, w=1):
        x1, y1, x2, y2 = self.poly.exterior.bounds
        vert_lines = [shapely.geometry.LineString([(x1, y1), (x1, y2)]),
                      shapely.geometry.LineString([(x2, y1), (x2, y2)])]

        vertical_shapes = [exterior(line, w) for line in vert_lines]
        inter = [shape.intersection(boundary_exterior) for shape in vertical_shapes]
        return to_multi(inter)

    def update_poly(self):
        self.poly = get_box(self.centroid, self.width, self.height)
        self.area = self.poly.area

    def _update_max_dim(self):
        self.max_dim = max(self.width, self.height)

    def reset(self, reset_max_dim=False):
        self.width = 1
        self.height = 1
        self.poly = get_box(self.centroid, self.width, self.height)
        self.area = self.poly.area
        if reset_max_dim:
            self._update_max_dim()


sleep_time = 0




def buffer(poly, amount=1):
    return poly.buffer(amount, join_style=2, cap_style=2)


def get_final_layout(rooms_lst, bathrooms_lst, inner_p, buffer_amount=2, fix=False, sleep=0.0, plot=True):
    living = buffer(inner_p, -buffer_amount).difference(GeometryCollection(
        [buffer(r.poly, buffer_amount) for r in rooms_lst if r.poly] + [buffer(b.poly, buffer_amount) for b in
                                                                        bathrooms_lst if b.poly]).buffer(0))

    if fix and not isinstance(living, Polygon):
        living = sorted(list(to_multi(living).geoms), key=lambda x: x.area, reverse=True)
        living, other = living[0], living[1:]
        for part in other:
            best_fit_min = 999999999
            best_fit = None
            for room in rooms_list + bathrooms_list:
                merged = MultiPolygon([part, room.poly]).envelope
                new_area = merged.area - room.poly.area
                if new_area < best_fit_min:
                    print(new_area, best_fit_min)
                    best_fit_min = new_area
                    best_fit = room

            best_fit.poly = MultiPolygon([part, best_fit.poly]).envelope

    # plot
    polys = [inner_p] + [living] + [room.poly for room in rooms_list if room.poly] + [bathroom.poly for bathroom in bathrooms_lst if bathroom.poly]
    # polys = [buffer(poly, buffer_amount) for poly in polys]
    series = gpd.GeoSeries(polys)

    if plot:
        ax.clear()
        pl = series.plot(cmap="Dark2", ax=ax)
        fig.canvas.draw()
        fig.canvas.flush_events()
        time.sleep(sleep)

    return series


rooms_list = [Room(centroid) for centroid in room_centroids]
bathrooms_list = [Room(centroid) for centroid in bathroom_centroids]

walls = exterior(inner_poly, 1)

for room in rooms_list:
    while not room.vert_intersection(walls) and not room.horiz_intersection(walls):
        room.increase_width()
        room.increase_height()
    get_final_layout(rooms_list, bathrooms_list, inner_poly, buffer_amount=2, fix=False, sleep=sleep_time)

    while room.vert_intersection(walls).length < room.height:
        room.increase_width()
    get_final_layout(rooms_list, bathrooms_list, inner_poly, buffer_amount=2, fix=False, sleep=sleep_time)

    while room.horiz_intersection(walls).length < room.width:
        room.increase_height()

get_final_layout(rooms_list, bathrooms_list, inner_poly, buffer_amount=2, fix=False, sleep=sleep_time)


for bathroom in bathrooms_list:
    while not bathroom.vert_intersection(walls) and not bathroom.horiz_intersection(walls):
        bathroom.increase_width()
        bathroom.increase_height()
    get_final_layout(rooms_list, bathrooms_list, inner_poly, buffer_amount=2, fix=False, sleep=sleep_time)

    while bathroom.vert_intersection(walls).length < bathroom.height:
        bathroom.increase_width()
    get_final_layout(rooms_list, bathrooms_list, inner_poly, buffer_amount=2, fix=False, sleep=sleep_time)

    while bathroom.horiz_intersection(walls).length < bathroom.width:
        bathroom.increase_height()
    get_final_layout(rooms_list, bathrooms_list, inner_poly, buffer_amount=2, fix=False, sleep=sleep_time)

# sort by max dimension

rooms_list.sort(key=lambda x: x.max_dim, reverse=False)
bathrooms_list.sort(key=lambda x: x.max_dim, reverse=False)

exteriors = []

[r.reset() for r in rooms_list]
[b.reset() for b in bathrooms_list]
get_final_layout(rooms_list, bathrooms_list, inner_poly, buffer_amount=2, fix=False, sleep=2)

for room in rooms_list:
    walls = exterior([inner_poly] + exteriors, 1)
    while not room.vert_intersection(walls) and not room.horiz_intersection(walls):
        room.increase_width()
        room.increase_height()
    get_final_layout(rooms_list, bathrooms_list, inner_poly, buffer_amount=2, fix=False, sleep=sleep_time)

    while room.vert_intersection(walls).length < room.height:
        room.increase_width()
    get_final_layout(rooms_list, bathrooms_list, inner_poly, buffer_amount=2, fix=False, sleep=sleep_time)

    while room.horiz_intersection(walls).length < room.width:
        room.increase_height()
    get_final_layout(rooms_list, bathrooms_list, inner_poly, buffer_amount=2, fix=False, sleep=sleep_time)

    exteriors.append(room.poly)

for bathroom in bathrooms_list:
    walls = exterior([inner_poly] + exteriors, 1)
    while not bathroom.vert_intersection(walls) and not bathroom.horiz_intersection(walls):
        bathroom.increase_width()
        bathroom.increase_height()
    get_final_layout(rooms_list, bathrooms_list, inner_poly, buffer_amount=2, fix=False, sleep=sleep_time)

    while bathroom.vert_intersection(walls).length < bathroom.height:
        bathroom.increase_width()
    get_final_layout(rooms_list, bathrooms_list, inner_poly, buffer_amount=2, fix=False, sleep=sleep_time)

    while bathroom.horiz_intersection(walls).length < bathroom.width:
        bathroom.increase_height()
    get_final_layout(rooms_list, bathrooms_list, inner_poly, buffer_amount=2, fix=False, sleep=sleep_time)

    exteriors.append(bathroom.poly)

for bathroom in bathrooms_list:
    width, height = bathroom.width, bathroom.height
    if width > height and width / height > 2:
        bathroom.height = width / 2
        bathroom.update_poly()

    elif height > width and height / width > 2:
        bathroom.width = height / 2
        bathroom.update_poly()



get_final_layout(rooms_list, bathrooms_list, inner_poly, buffer_amount=2, fix=False, sleep=sleep_time)


s = get_final_layout(rooms_list, bathrooms_list, inner_poly, buffer_amount=2, fix=True, plot=True, sleep=100)

