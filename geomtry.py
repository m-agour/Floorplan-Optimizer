import time

import matplotlib
from shapely import GeometryCollection, box, MultiPolygon, LineString, unary_union
from shapely.geometry import Polygon, Point
import re
import os

os.environ['USE_PYGEOS'] = '0'
import geopandas as gpd
import matplotlib.pyplot as plt

plot_i = 0

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


def buffer(poly, amount=1.0):
    return poly.buffer(amount, join_style=2, cap_style=2)


def aspect(poly):
    width, height = poly.bounds[2] - poly.bounds[0], poly.bounds[3] - poly.bounds[1]
    return max(width, height) / min(width, height)


def get_small_segments(polygon):
    segments = []
    xs, ys = polygon.exterior.xy
    for i, x in enumerate(xs):
        line = LineString([(x, ys[i] - 10), (x, ys[i] + 10)]).buffer(0.0001, join_style=2, cap_style=2)
        diff = polygon.difference(line)
        if isinstance(diff, MultiPolygon):
            [segments.append(i) for i in diff.geoms]
    for i, y in enumerate(ys):
        line = LineString([(xs[i] - 10, y), (xs[i] + 10, y)]).buffer(0.0001, join_style=2, cap_style=2)
        diff = polygon.difference(line)
        if isinstance(diff, MultiPolygon):
            [segments.append(i) for i in diff.geoms]

    segments.sort(key=lambda poly: poly.area, reverse=True)
    segments = list(
        filter(lambda poly: poly.area < polygon.area / 20 and poly.buffer(2).difference(
            polygon).area and aspect(poly) > 4, segments))

    return segments


def get_walls(poly, width=2.5):
    return buffer(poly, width).difference(poly)


def fix_floor_plan(inner_p, bedrooms_lst, bathrooms_lst, door, buffer_amount=2, plot=0.0):
    living = buffer(inner_p, -buffer_amount).difference(GeometryCollection(
        [buffer(r.poly, buffer_amount) for r in bedrooms_lst if r.poly] + [buffer(b.poly, buffer_amount) for b in
                                                                           bathrooms_lst if b.poly]).buffer(0))

    if not isinstance(living, Polygon):
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

            if plot:
                get_final_layout(inner_p, bedrooms_lst, bathrooms_lst, door, buffer_amount=2, plot=plot)

    segments = get_small_segments(living)

    for seg in segments:
        best_fit_room = None
        best_fit_area = 0
        seg_buf = buffer(seg, 2)
        for room in bathrooms_lst + bedrooms_lst:
            room_buf = buffer(room.poly, 2)
            inter = room_buf.intersection(seg_buf)
            inter_area = inter.area
            if room.type == "bedroom":
                inter_area *= 1.2
            if inter and inter_area > best_fit_area:
                best_fit_room = room
                best_fit_area = inter_area

        if best_fit_room is not None:
            best_fit_room.poly = buffer(buffer(best_fit_room.poly, 2).union(buffer(seg_buf, -1)), -2)
            living = living.difference(seg)

            if plot:
                get_final_layout(inner_p, bedrooms_lst, bathrooms_lst, door, buffer_amount=2, plot=plot)

    for i in range(len(bedrooms_lst) - 1):
        for j in range(i + 1, len(bedrooms_lst)):
            room_1 = bedrooms_lst[i]
            room_2 = bedrooms_lst[j]
            if room_1.poly.area < room_2.poly.area:
                room_2.poly = room_2.poly.difference(buffer(room_1.poly, 2))
            else:
                room_1.poly = room_1.poly.difference(buffer(room_2.poly, 2))

            if plot:
                get_final_layout(inner_p, bedrooms_lst, bathrooms_lst, door, buffer_amount=2, plot=plot)

    bed_polys = unary_union([room.poly for room in bedrooms_lst if room.poly]).buffer(0)
    bath_polys = unary_union([room.poly for room in bathrooms_lst if room.poly]).buffer(0)
    bed_walls = unary_union([get_walls(room.poly) for room in bedrooms_lst if room.poly]).buffer(0)
    bath_walls = unary_union([get_walls(room.poly) for room in bathrooms_lst if room.poly]).buffer(0)
    living_wall = get_walls(living)

    bed_walls = bed_walls.difference(bath_polys).buffer(0).difference(bed_polys).buffer(0)
    living_wall = living_wall.difference(bed_polys).difference(bath_polys).buffer(0)

    walls = unary_union([living_wall, bed_walls, bath_walls]).buffer(0)

    polys = [unary_union(plst) for plst in [[living], [door], buffer(bed_polys, 1), buffer(bath_polys, 1), walls]]
    series = gpd.GeoSeries(polys)

    if plot:
        plot_series(series, sleep=plot)

    return polys


def plot_series(series, sleep=1.0):
    global plot_i
    ax.clear()
    series.plot(cmap="Dark2", ax=ax)
    fig.canvas.draw()
    fig.canvas.flush_events()
    plt.savefig(f"imgs/{str(plot_i).zfill(3)}.png", dpi=300)
    plot_i += 1
    time.sleep(sleep)


def get_final_layout(inner_p, bedrooms_lst, bathrooms_lst, front, buffer_amount=2, plot=0.0, fix=True):
    living = buffer(inner_p, -buffer_amount).difference(GeometryCollection(
        [buffer(r.poly, buffer_amount) for r in bedrooms_lst if r.poly] + [buffer(b.poly, buffer_amount) for b in
                                                                           bathrooms_lst if b.poly]).buffer(0))

    polys = [living, front] + [room.poly for room in bedrooms_lst if room.poly] + [room.poly for room in bathrooms_lst
                                                                                   if
                                                                                   room.poly]
    series = gpd.GeoSeries(polys)

    if plot:
        plot_series(series, plot)
    return series
