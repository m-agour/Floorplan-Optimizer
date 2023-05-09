import time

import matplotlib
from shapely import GeometryCollection, box, MultiPolygon, LineString
from shapely.geometry import Polygon, Point
import re
import os
os.environ['USE_PYGEOS'] = '0'
import geopandas as gpd
import matplotlib.pyplot as plt


matplotlib.use('Qt5Agg')
plt.ion()
fig, ax = plt.subplots()
plt.show()


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


def get_box(centroid, width, height):
    x, y = centroid.coords[0]
    return box(x - width / 2, y - height / 2, x + width / 2, y + height / 2)


def parse_points(input_str):
    # Extract the coordinate pairs using regex
    coords_str = re.findall(r'\((\d+)\s(\d+)\)', input_str)

    # Convert coordinate pairs to Shapely Points and store them in a list
    points = [Point(int(x), int(y)) for x, y in coords_str]

    return points


def buffer(poly, amount=1):
    return poly.buffer(amount, join_style=2, cap_style=2)


def get_final_layout(inner_p, bedrooms_lst, bathrooms_lst, buffer_amount=2, fix=False, sleep=0.0, plot=True):
    living = buffer(inner_p, -buffer_amount).difference(GeometryCollection(
        [buffer(r.poly, buffer_amount) for r in bedrooms_lst if r.poly] + [buffer(b.poly, buffer_amount) for b in
                                                                           bathrooms_lst if b.poly]).buffer(0))

    if fix and not isinstance(living, Polygon):
        living = sorted(list(to_multi(living).geoms), key=lambda x: x.area, reverse=True)
        living, other = living[0], living[1:]
        for part in other:
            best_fit_min = float("inf")
            best_fit = None
            for room in bedrooms_lst + bathrooms_lst:
                merged = MultiPolygon([part, room.poly]).envelope
                new_area = merged.area - room.poly.area
                if new_area < best_fit_min:
                    best_fit_min = new_area
                    best_fit = room

            best_fit.poly = MultiPolygon([part, best_fit.poly]).envelope

    polys = [inner_p] + [living] + [room.poly for room in bedrooms_lst if room.poly] + [bathroom.poly for bathroom in
                                                                                        bathrooms_lst if bathroom.poly]
    series = gpd.GeoSeries(polys)
    if plot:
        ax.clear()
        series.plot(cmap="Dark2", ax=ax)
        fig.canvas.draw()
        fig.canvas.flush_events()
        time.sleep(sleep)
    return series
