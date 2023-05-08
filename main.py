import numpy as np
import shapely
from scipy.spatial import Voronoi, voronoi_plot_2d
import matplotlib.pyplot as plt
from shapely import GeometryCollection, box, MultiPolygon
from shapely.geometry import Polygon, Point
import re

import geopandas as gpd


def exterior(poly, w=2):
    if isinstance(poly, Polygon):
        return poly.exterior.buffer(w, join_style=2, cap_style=2)
    elif isinstance(poly, MultiPolygon):
        return MultiPolygon([p.exterior.buffer(w, join_style=2, cap_style=2) for p in poly.geoms])


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
alle = gpd.GeoSeries([inner_poly,
                      door_poly,
                      inner_poly,
                      GeometryCollection(room_centroids),
                      GeometryCollection(bathroom_centroids)])
alle.plot(cmap="Dark2")

plt.show()

import random
from deap import base, creator, tools


# Define the objective function to maximize the total area of the rooms
def objective_function(individual):
    score = 0
    rooms_boxes = [get_box(room_centroids[i], individual[i], individual[i + no_rooms]) for i in range(no_rooms)]
    bathrooms_boxes = [get_box(bathroom_centroids[i], individual[i + no_rooms * 2], individual[i + no_rooms * 3]) for i
                       in range(no_bathrooms)]

    w = 2
    rooms_exteriors = [exterior(i, w) for i in rooms_boxes]
    bathrooms_exteriors = [exterior(i, w) for i in bathrooms_boxes]

    inner_exterior = exterior(inner_poly, w)

    total_area = 0

    living = inner_poly.difference(MultiPolygon(rooms_boxes + bathrooms_boxes).buffer(0))
    living_exterior = exterior(living, w).buffer(0)
    if isinstance(living, MultiPolygon):
        score -= 10000

    # compactness of living room
    living_compactness = living.area / living.length
    score += living_compactness * 10000

    for i in range(no_rooms):
        room_box = rooms_boxes[i]
        room_exterior = rooms_exteriors[i]
        area = room_box.area
        inner_area = inner_poly.intersection(room_box).area
        score += inner_area * 3
        score -= (area - inner_area) ** 3
        total_area += area

        room_exterior = room_exterior.difference(inner_exterior)
        if room_exterior:
            score += 150 * room_exterior.area  # Increase weight for rooms touching boundary

        for bathroom_box in bathrooms_boxes:
            if room_box.intersects(bathroom_box):
                score += 150  # Increase weight for rooms touching bathrooms

        living_room = living_exterior.intersection(room_exterior.buffer(0))
        if not living_room:
            score -= 1500000

        score += living_room.area * 100

    min_room_area = min([room_box.area for room_box in rooms_boxes])

    for i in range(no_bathrooms):
        bathroom_box = bathrooms_boxes[i]
        bath_exterior = bathrooms_exteriors[i]

        area = bathroom_box.area
        inner_area = bathroom_box.intersection(inner_poly).area
        score += inner_area * 2
        score -= (area - inner_area) ** 3
        total_area += area

        if bathroom_box.area > min_room_area:
            score -= 150000

        for room_box in rooms_boxes:
            if bathroom_box.intersects(room_box):
                score += 20

        bath_exterior_inter = bath_exterior.difference(inner_exterior)
        if bath_exterior_inter:
            score += 150 * bath_exterior_inter.area  # Increase weight for rooms touching boundary
    return score,


# Create the optimization problem
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("attr_float", random.uniform, 30, 70)  # Assuming min and max dimensions are 1 and 10
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_float,
                 n=(len(room_centroids) + len(bathroom_centroids)) * 2)  # n = 2 * number of rooms
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# Define genetic operators
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.1)
toolbox.register("select", tools.selBest)
toolbox.register("evaluate", objective_function)


# Run the Genetic Algorithm
def main():
    pop = toolbox.population(n=50, )  # Population size
    CXPB, MUTPB, NGEN = 0.5, 0.2, 20  # Crossover, mutation probabilities, and number of generations

    # Evaluate the entire population
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    for g in range(NGEN):
        # Select the next generation individuals
        offspring = toolbox.select(pop, len(pop))
        offspring = list(offspring)

        # Apply crossover and mutation
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXPB:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        # Evaluate the offspring
        fitnesses = list(map(toolbox.evaluate, offspring))
        for ind, fit in zip(offspring, fitnesses):
            ind.fitness.values = fit

        # Replace the old population by the offspring
        pop[:] = offspring

    best_ind = tools.selBest(pop, 1)[0]
    return best_ind


best_solution = main()
print("Best solution: ", best_solution)

# Plot the best solution
bed_boxes = [get_box(room_centroids[i], best_solution[2 * i], best_solution[2 * i + 1]) for i in range(no_rooms)]
bath_boxes = [
    get_box(bathroom_centroids[i], best_solution[2 * no_rooms + 2 * i], best_solution[2 * no_rooms + 2 * i + 1]) for i
    in range(no_bathrooms)]


new_alle = gpd.GeoSeries(
    [exterior(i) for i in [door_poly, inner_poly, MultiPolygon(bed_boxes), MultiPolygon(bath_boxes)]])
new_alle.plot(cmap="Dark2")
plt.show()
