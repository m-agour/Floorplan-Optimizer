import time

from shapely import LineString, MultiPolygon, GeometryCollection
from algorithm import optimize
from geomtry import get_final_layout, fix_floor_plan, plot_series
from room import get_rooms
from data import data
import geopandas as gpd


# for plan in [list(data.keys())[-1]]:
    # plan = 'plan11.fy'
for plan in data:
    t = time.time()
    bedrooms_centroids = data[plan]['bedroom']
    bathroom_centroids = data[plan]['bathroom']
    front = data[plan]['front']
    boundary = data[plan]['boundary']
    bedrooms_list = get_rooms(bedrooms_centroids, typ="bedroom")
    bathrooms_list = get_rooms(bathroom_centroids, typ="bathroom")

    init_series = gpd.GeoSeries([boundary, front] +
                                [GeometryCollection(bedrooms_centroids),
                                GeometryCollection(bathroom_centroids)])


    bedrooms, bathrooms = optimize(boundary, bedrooms_list, bathrooms_list, front, plot=0.1)
    polys = fix_floor_plan(boundary, bedrooms, bathrooms, front, plot=0.0)
    series = gpd.GeoSeries(polys)

