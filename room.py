import shapely

from geomtry import get_box, exterior, to_multi


class Room:
    def __init__(self, center=None, width=1, height=1):
        self.width = width
        self.height = height
        self.centroid = center
        self.poly = get_box(self.centroid, self.width, self.height)
        self.area = 0
        self.max_dim = 0
        self.min_dim = 0
        self._update_min_max_dim()

    def increase_width(self, amount=0.1):
        self.width += amount
        self.poly = get_box(self.centroid, self.width, self.height)
        self.area = self.poly.area
        self._update_min_max_dim()

    def increase_height(self, amount=0.1):
        self.height += amount
        self.poly = get_box(self.centroid, self.width, self.height)
        self.area = self.poly.area
        self._update_min_max_dim()

    def set_width(self, width):
        self.width = width
        self.poly = get_box(self.centroid, self.width, self.height)
        self.area = self.poly.area
        self._update_min_max_dim()

    def set_height(self, height):
        self.height = height
        self.poly = get_box(self.centroid, self.width, self.height)
        self.area = self.poly.area
        self._update_min_max_dim()

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

    def _update_min_max_dim(self):
        self.max_dim = max(self.width, self.height)
        self.min_dim = min(self.width, self.height)

    def reset(self, reset_max_dim=False):
        self.width = 1
        self.height = 1
        self.poly = get_box(self.centroid, self.width, self.height)
        self.area = self.poly.area
        if reset_max_dim:
            self._update_min_max_dim()


def get_rooms(rooms_centroids):
    rooms_lst = [Room(centroid) for centroid in rooms_centroids]
    return rooms_lst
