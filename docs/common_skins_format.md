# Common skins format

"Common skin format" is convention on how individual tiles are placed in skin image.

| tessellation | common skin format     | skin image example |
| ------------ | ---------------------- | ------------------ |
| Sokoban      | ![Sokoban skin format] | ![Sokoban skin]    |

Skin tries to guess individual tile dimensions and position from whole image width
and height. This guesswork requires that all tiles in image are squares. The only
exception for this rule are some older 4x4 Sokoban skins that are allowed to have
rectangular tiles:

| Sokoban rectangular skin    |
| --------------------------- |
| ![Sokoban rectangular skin] |

There is no similar "standard" for other tessellations (Hexoban, Trioban, ...) so
libsokoengine implements it's own.

Bounding box of regular hexagon and equilateral triangle is not square.
libsokoengine still requires that individual tiles are square. Actual tile images
should then be aligned to bottom left of each square tile:

| tessellation | common skin format     | skin image example |
| ------------ | ---------------------- | ------------------ |
| Hexoban      | ![Hexoban skin format] | ![Hexoban skin]    |
| Trioban      | ![Trioban skin format] | ![Trioban skin]    |

- regular triangles in Trioban skins must be aligned to bottom of bounding tile
  square and width of triangle must be width of bounding square tile.
- regular hexagons in Hexoban skins must be aligned to left of bounding tile
  square and height of hexagon must be height of bounding square.
- grid in below images is for illustration purposes only, and should not be present
  in final skin image
- last pixel in image is grid pixel and image for ie. Hexoban is of width
  300px. This is intentional. In final image, although the grid is not visible, we
  still want whole image to be 300px wide (like there was a grid in image). Common
  mistake is to remove grid before exporting skin design into skin image and then
  end up with image that is 299px wide. That image fails Skin tile processing.
  Same reasoning can be applied to Trioban image top row.
  When making skins for these 2 variants in ie. InkScape, it is best to include the
  grid object in .png export, but set opacity of grid stroke to zero. That way, grid
  pixels will be preserved but transparent in final .png image.

See also: <a href="YASC_Skin_Tutorial_1_02.pdf" target="_blank">YASC skin tutorial</a>

[Sokoban skin format]: ./skin_format/sokoban_common_skins_format.png "Sokoban common skins format"
[Sokoban skin]: ./skin_format/sokoban_skin.png "Example Sokoban skin"
[Sokoban rectangular skin]: ./skin_format/rectangular_skin.png "Sokoban skin with rectangular tiles"
[Hexoban skin format]: ./skin_format/hexoban_common_skins_format.png "Hexoban common skins format"
[Hexoban skin]: ./skin_format/hexoban_skin.png "Example Hexoban skin"
[Trioban skin format]: ./skin_format/trioban_common_skins_format.png "Trioban common skins format"
[Trioban skin]: ./skin_format/trioban_skin.png "Example Trioban skin"
