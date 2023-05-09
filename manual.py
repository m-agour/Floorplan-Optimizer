from algorithm import optimize
from geomtry import get_final_layout
from room import get_rooms
from data import data


for plan in [list(data.keys())[-1]]:
    bedrooms_centroids = data[plan]['bedroom']
    bathroom_centroids = data[plan]['bathroom']
    front = data[plan]['front']
    boundary = data[plan]['boundary']
    bedrooms_list = get_rooms(bedrooms_centroids)
    bathrooms_list = get_rooms(bathroom_centroids)
    bedrooms, bathrooms = optimize(boundary, bedrooms_list, bathrooms_list, front)
    get_final_layout(boundary, bedrooms, bathrooms, buffer_amount=2, sleep=40, fix=True)



