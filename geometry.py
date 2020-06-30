"""
Jonas Nockert (2020)

Point and rectangle classes where a point represent an individual and
a rectangle some sort of social grouping.

"""
import math


class Point:

    def __init__(self, x_0=0, y_0=0):
        self._x = x_0
        self._y = y_0

    @classmethod
    def fromlist(cls, coords):
        assert len(coords) == 2
        return cls(coords[0], coords[1])

    def __repr__(self):
        return "Point(%s, %s)" % (self._x, self._y)

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def as_tuple(self):
        return (self._x, self._y)

    def distance(self, other_point):
        return math.sqrt((self.x - other_point.x) ** 2 + (self.y - other_point.y) ** 2)


class Rect:
    def __init__(self, xmin_0=0, xmax_0=0, ymin_0=0, ymax_0=0):
        self._xmin = xmin_0
        self._xmax = xmax_0
        self._ymin = ymin_0
        self._ymax = ymax_0

    def __repr__(self):
        return "Rect(%s-%s, %s-%s)" % (self._xmin, self._xmax, self._ymin, self._ymax)

    @property
    def upper_left(self):
        return Point(self._xmin, self._ymin)

    @property
    def lower_right(self):
        return Point(self._xmax, self._ymax)

    @property
    def xmin(self):
        return self._xmin

    @property
    def xmax(self):
        return self._xmax

    @property
    def ymin(self):
        return self._ymin

    @property
    def ymax(self):
        return self._ymax

    @property
    def width(self):
        return self._xmax - self._xmin + 1

    @property
    def height(self):
        return self._ymax - self._ymin + 1

    @property
    def center(self):
        return Point(self._xmin + self.width // 2, self._ymin + self.height // 2)

    def area(self):
        return self.width * self.height

    @property
    def ratio_wh(self):
        assert self.height > 0
        return self.width / self.height

    @property
    def ratio_hw(self):
        assert self.width > 0
        return self.height / self.width

    def get_points(self):
        points = []
        for x in range(self._xmin, self._xmax + 1):
            for y in range(self._ymin, self._ymax + 1):
                points.append(Point(x, y))
        return points
