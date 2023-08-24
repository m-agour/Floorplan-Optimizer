Here is a draft README for this floor plan optimization repo:

# Floorplan Optimizer

This repository contains code to optimize the layout and dimensions of rooms for a floorplan layout bounded by a polygon.


https://github.com/m-agour/Width-Height-FloorPlan/assets/63170874/62197974-6d9d-4310-b9fe-97ec5b9415fd


## Overview

The core optimization logic is in `algorithm.py`. It takes as input:

- Floorplan boundary polygon 
- Bedroom polygon centroids
- Bathroom polygon centroids

It outputs the optimized bedroom and bathroom polygons. 

The main steps are:

- Initialize rooms at centroids 
- Grow room widths & heights outwards until hitting walls
- Post-process rooms to be more rectangular

`data.py` contains sample floorplan data to use.

`geomtry.py` has helper geometry functions.

`room.py` defines the Room class to represent each room.

## Usage

Run optimization on a sample floorplan:

```python
from algorithm import optimize
from data import data

fp = data['simple.txt']
bedrooms = get_rooms(fp['bedroom']) 
bathrooms = get_rooms(fp['bathroom'])

opt_beds, opt_baths = optimize(fp['boundary'], bedrooms, bathrooms)
```

## Installation

```
pip install -r requirements.txt
```

Requires Python 3 and dependencies in `requirements.txt`.

## Contributing

Contributions to improve the optimization algorithm are welcome! 

Open issues for any bugs or requests. Pull requests are appreciated.
