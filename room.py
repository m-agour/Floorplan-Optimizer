import shapely
from shapely.affinity import scale

from geomtry import get_box, exterior, to_multi


class Room:
    def __init__(self, center=None, width=1, height=1, typ='bedroom'):
        self.type = typ
        self.width = width
        self.height = height
        self.centroid = center
        self.poly = get_box(self.centroid, self.width, self.height)
        self.area = 0
        self.max_dim = 0
        self.min_dim = 0
        self.is_width_min = 0
        self.backup_max_dim = 0
        self.backup_min_dim = 0
        self.backup_is_width_min = 0
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

    def increase_width_height(self, amount=1):
        self.width += amount
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
        if self.width < self.height:
            self.max_dim = self.height
            self.min_dim = self.width
            self.is_width_min = True
        else:
            self.min_dim = self.height
            self.max_dim = self.width
            self.is_width_min = False

    def reset(self, reset_max_dim=False, backup=True):
        self.width = 1
        self.height = 1
        self.poly = get_box(self.centroid, self.width, self.height)
        self.area = self.poly.area
        if reset_max_dim:
            self._update_min_max_dim()
        if backup:
            self.backup_min_max()

    def backup_min_max(self):
        self.backup_min_dim = self.min_dim
        self.backup_max_dim = self.max_dim
        self.backup_is_width_min = self.is_width_min

    def restore(self, min_thresh=0, max_thresh=float('inf'), default=5):
        width, height = (self.backup_min_dim, self.backup_max_dim) if \
            self.is_width_min else (self.backup_max_dim, self.backup_min_dim)
        minimum = min(width, height)
        if minimum < min_thresh or minimum > max_thresh:
            minimum = default
        else:
            minimum /= 2

        if width < min_thresh or width > max_thresh:
            width = minimum
        if height < min_thresh or height > max_thresh:
            height = minimum
        self.set_width(width)
        self.set_height(height)

    def expand_until_intersection(self, target, width=1, height=1, increment=1, threshold=0.0):
        current_polygon = self.poly
        x_scale, y_scale = 1, 1
        if width:
            x_scale = 1 + increment if width else 1
        if height:
            y_scale = 1 + increment if height else 1
        while not current_polygon.intersection(target).area >= threshold:
            current_polygon = scale(current_polygon, xfact=x_scale, yfact=y_scale, origin='centroid')
        bounds = current_polygon.bounds
        self.width, self.height = bounds[2] - bounds[0], bounds[3] - bounds[1]
        self.poly = current_polygon
        self.area = current_polygon.area
        self._update_min_max_dim()
        return current_polygon


def get_rooms(rooms_centroids, typ="bedroom"):
    rooms_lst = [Room(centroid, typ=typ) for centroid in rooms_centroids]
    return rooms_lst
