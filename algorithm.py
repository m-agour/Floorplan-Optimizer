from geomtry import exterior, get_final_layout


def _room_width_height_march(room, inner, walls, buf_size, append_walls=False):
    if append_walls:
        walls_p = exterior([inner] + walls, buf_size)
    else:
        walls_p = exterior(inner, buf_size)

    while not room.vert_intersection(walls_p) and not room.horiz_intersection(walls_p):
        room.increase_width()
        room.increase_height()
    while room.vert_intersection(walls_p).length < room.height:
        room.increase_width()
    while room.horiz_intersection(walls_p).length < room.width:
        room.increase_height()
    if append_walls:
        walls.append(room.poly)
    return walls


def march_dims(rooms_lst, inner, walls, buf_size, append_walls=False):
    for room in rooms_lst:
        walls = _room_width_height_march(room, inner, walls, buf_size, append_walls)
    return walls


def optimize(inner, bedrooms_lst, bathrooms_lst, door=None, step=0.5):
    walls = exterior(inner, step)
    march_dims(bedrooms_lst, inner, walls, step)
    march_dims(bathrooms_lst, inner, walls, step)

    bedrooms_lst.sort(key=lambda x: x.max_dim, reverse=False)
    bathrooms_lst.sort(key=lambda x: x.max_dim, reverse=False)

    [r.reset() for r in bedrooms_lst]
    [b.reset() for b in bathrooms_lst]

    walls = []
    walls = march_dims(bedrooms_lst, inner, walls, step, append_walls=True)
    walls = march_dims(bathrooms_lst, inner, walls, step, append_walls=True)

    for bathroom in bathrooms_lst:
        width, height = bathroom.width, bathroom.height
        if width > height and width / height > 2:
            bathroom.height = width / 2
            bathroom.update_poly()

        elif height > width and height / width > 2:
            bathroom.width = height / 2
            bathroom.update_poly()
    return bedrooms_lst, bathrooms_lst
