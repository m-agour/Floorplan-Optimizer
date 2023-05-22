import time

# from dims_optimizer.geomtry import exterior, get_final_layout, buffer
from dims_optimizer.geomtry import exterior, get_final_layout, buffer


def _room_width_height_march(room, inner, walls, buf_size, append_walls=False, plot=0, bed_bath_data=[]):
    if append_walls:
        walls_p = exterior([inner] + walls, buf_size)
    else:
        walls_p = exterior(inner, buf_size)

    if plot:
        get_final_layout(inner, bed_bath_data[0], bed_bath_data[1], bed_bath_data[2], buffer_amount=2, plot=plot, fix=False)

    while not room.vert_intersection(walls_p) and not room.horiz_intersection(walls_p):
        room.increase_width_height(buf_size)
    if plot:
        get_final_layout(inner, bed_bath_data[0], bed_bath_data[1], bed_bath_data[2], buffer_amount=2, plot=plot, fix=False)

    if not room.vert_intersection(walls_p):
        while room.vert_intersection(walls_p).length < room.width / 5:
            room.increase_width(buf_size)
    else:
        while room.horiz_intersection(walls_p).length < room.height / 5:
            room.increase_height(buf_size)

    if plot:
        get_final_layout(inner, bed_bath_data[0], bed_bath_data[1], bed_bath_data[2], buffer_amount=2, plot=plot, fix=False)

    if append_walls:
        walls.append(room.poly)
    return walls


def march_dims(rooms_lst, inner, walls, buf_size, append_walls=False, plot=0, bed_bath_data=[]):
    for room in rooms_lst:
        walls = _room_width_height_march(room, inner, walls, buf_size, append_walls, plot, bed_bath_data)
    return walls


def optimize(inner, bedrooms_lst, bathrooms_lst, door=None, step=1, plot=0):
    t = time.time()
    walls = exterior(inner, step)
    bed_bath_data = [bedrooms_lst, bathrooms_lst, door]
    print("Time to exterior: ", time.time() - t)
    t = time.time()
    march_dims(bedrooms_lst, inner, walls, step, plot=plot, bed_bath_data=bed_bath_data)
    walls = exterior(inner, step)
    march_dims(bathrooms_lst, inner, walls, step, plot=plot, bed_bath_data=bed_bath_data)
    print("Time to optimize: ", time.time() - t)
    t = time.time()
    bedrooms_lst.sort(key=lambda x: x.min_dim * x.max_dim, reverse=False)
    bathrooms_lst.sort(key=lambda x: x.min_dim * x.max_dim, reverse=False)
    print("Time to sort: ", time.time() - t)
    t = time.time()
    if plot:
        get_final_layout(inner, bed_bath_data[0], bed_bath_data[1], bed_bath_data[2], buffer_amount=2, plot=plot, fix=False)

    [r.reset() for r in bedrooms_lst]

    if plot:
        get_final_layout(inner, bed_bath_data[0], bed_bath_data[1], bed_bath_data[2], buffer_amount=2, plot=plot, fix=False)

    if plot:
        get_final_layout(inner, bed_bath_data[0], bed_bath_data[1], bed_bath_data[2], buffer_amount=2, plot=plot, fix=False)

    walls = []
    walls = march_dims(bedrooms_lst, inner, walls, step, append_walls=True, plot=plot, bed_bath_data=bed_bath_data)
    # walls = march_dims(bathrooms_lst, inner, walls, step, append_walls=True, plot=plot, bed_bath_data=bed_bath_data)


    mean_bed_area = sum([b.poly.area for b in bedrooms_lst]) / len(bedrooms_lst)
    mean_bed_min_dim = sum([b.min_dim for b in bedrooms_lst]) / len(bedrooms_lst)
    mean_bed_max_dim = sum([b.max_dim for b in bedrooms_lst]) / len(bedrooms_lst)

    good_bathes = [i for i in bathrooms_lst if i.poly.area < mean_bed_area * 0.7]
    bad_bathes = [i for i in bathrooms_lst if i not in good_bathes]
    [b.reset() for b in bad_bathes]
    for b in good_bathes:
        b.poly = buffer(b.poly, -2)
    walls = march_dims(bad_bathes, inner, walls, step, append_walls=True, plot=plot, bed_bath_data=bed_bath_data)


    for bathroom in bathrooms_lst:
        width, height = bathroom.width, bathroom.height
        if width > height and width / height > 2:
            bathroom.height = width / 2
            bathroom.update_poly()

        elif height > width and height / width > 2:
            bathroom.width = height / 2
            bathroom.update_poly()

        if plot:
            get_final_layout(inner, bed_bath_data[0], bed_bath_data[1], bed_bath_data[2], buffer_amount=2, plot=plot / 3, fix=False)

    bad_bathrooms = [b for b in bathrooms_lst if b.area < mean_bed_area / 20]
    for bad_bath in bad_bathrooms:
        if bad_bath.backup_min_dim <= mean_bed_min_dim * 0.8:
            bad_bath.restore(min_thresh=mean_bed_min_dim * 0.3, max_thresh=mean_bed_min_dim * 0.7)

        if plot:
            get_final_layout(inner, bed_bath_data[0], bed_bath_data[1], bed_bath_data[2], buffer_amount=2, plot=plot / 3, fix=False)

    get_final_layout(inner, bed_bath_data[0], bed_bath_data[1], bed_bath_data[2], buffer_amount=2, plot=plot * 4, fix=False)
    print("Time to reset: ", time.time() - t)

    return bedrooms_lst, bathrooms_lst
