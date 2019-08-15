from enum import IntEnum


class CellOrientation(IntEnum):
    """
    Dynamic board cell property that depends on cell position in some tessellations.
    ie. in Trioban, coordinate origin is triangle pointing upwards. This means that
    orientation of all other triangles depends on their position. Methods that
    calculate orientation return one of these values.

    See Also:
        :meth:`.TessellationBase.cell_orientation`
    """

    DEFAULT = 0
    TRIANGLE_DOWN = 1
    OCTAGON = 2
