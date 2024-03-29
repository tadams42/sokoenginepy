import enum


class TileShape(enum.Enum):
    """
    Dynamic board cell property that depends on cell position in some tessellations.
    ie. in Trioban, origin of coordinate system is triangle pointing upwards. Shape of
    all other triangles depends on orientation of origin.
    """

    DEFAULT = 0
    TRIANGLE_DOWN = 1
    OCTAGON = 2
