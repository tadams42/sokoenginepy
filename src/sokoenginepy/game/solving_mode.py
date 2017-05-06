from enum import IntEnum


class SolvingMode(IntEnum):
    FORWARD = 0
    REVERSE = 1

    def __repr__(self):
        return "SolvingMode." + self.name
