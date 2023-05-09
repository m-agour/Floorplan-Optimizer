import os
import shapely

from geomtry import parse_points


def load_plan(file_name):
    with open(file_name, 'r') as f:
        strings = f.read()
        bed, bath, front, boundary = strings.split('\n')
        bed = parse_points(bed)
        bath = parse_points(bath)
        front = shapely.from_wkt(front)
        boundary = shapely.from_wkt(boundary)
        return {'bedroom': bed, 'bathroom': bath, 'front': front, 'boundary': boundary}


files = os.listdir('plans')
data = {}
for file in files:
    data[file] = load_plan(os.path.join('plans', file))
