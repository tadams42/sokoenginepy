# Animation and graph debugging requirements
# 'scipy >= 0.18.0',
# 'moviepy >= 0.2.0',
# 'matplotlib >= 1.5.0',

from functools import partial

import numpy as np
from moviepy.editor import ImageSequenceClip

from ..core import Tessellation, X, Y, index_1d
from ..input_output import parse_board_string


def animate_board_graph_reachables(output_gif_path="/tmp/reachables.gif"):
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (128, 128, 128)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)

    animation_frames = []

    board_str = "\n".join([
        # 123456789012345678
        "    #####",  # 0
        "    #   #",  # 1
        "    #$  #",  # 2
        "  ###  $##",  # 3
        "  #  $ $ #",  # 4
        "### # ## #   ######",  # 5
        "#   # ## #####  ..#",  # 6
        "# $  $          ..#",  # 7
        "##### ### #@##  ..#",  # 8
        "    #     #########",  # 9
        "    #######",  # 10
    ])
    board_cells = parse_board_string(board_str)
    width = 19
    height = 11
    root = index_1d(11, 8, width)
    bg = BoardGraph(width * height, GraphType.DIRECTED)
    bg.reconfigure_edges(width, height, SokobanTessellation())

    for y, row in enumerate(board_cells):
        for x, chr in enumerate(row):
            bg[index_1d(x, y, width)] = BoardCell(chr)

    def add_animation_frame(
        current_position, reachables, to_inspect, excluded, frames, width,
        height
    ):
        row_data = width * [WHITE]
        matrix = np.array(height * [row_data])

        for i in reachables:
            x, y = X(i, width), Y(i, width)
            matrix[y, x] = GREEN

        for i in to_inspect:
            x, y = X(i, width), Y(i, width)
            matrix[y, x] = GRAY

        for i in excluded:
            x, y = X(i, width), Y(i, width)
            matrix[y, x] = BLACK

        x, y = X(current_position, width), Y(current_position, width)
        matrix[y, x] = RED

        frames.append(matrix)

    bg.reachables(
        root,
        add_animation_frame_hook=partial(
            add_animation_frame,
            width=width,
            height=height,
            frames=animation_frames
        )
    )

    animation.write_gif(output_gif_path)
