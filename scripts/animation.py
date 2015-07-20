import numpy as np
from moviepy.editor import ImageSequenceClip
from functools import partial
from sokoengine.variant.variant_board import VariantBoard
from sokoengine.variant.tessellation import INDEX, X, Y

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)


def animate_board_graph_reachables(output_gif_path="/tmp/reachables.gif"):
    animation_frames = []

    board_str = "\n".join([
        # 123456789012345678
        "    #####",            # 0
        "    #   #",            # 1
        "    #$  #",            # 2
        "  ###  $##",           # 3
        "  #  $ $ #",           # 4
        "### # ## #   ######",  # 5
        "#   # ## #####  ..#",  # 6
        "# $  $          ..#",  # 7
        "##### ### #@##  ..#",  # 8
        "    #     #########",  # 9
        "    #######",          # 10
    ])
    vb = VariantBoard(board_str = board_str)
    width = vb.width
    height = vb.height
    root = INDEX(11, 8, width)

    def add_animation_frame(
        current_position, reachables, to_inspect, excluded, frames, width, height
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

    vb._reachables(
        root,
        add_animation_frame_hook=partial(
            add_animation_frame,
            width=width, height=height, frames=animation_frames
        )
    )

    animation = ImageSequenceClip(animation_frames, fps=2)
    animation.write_gif(output_gif_path)

animate_board_graph_reachables()
