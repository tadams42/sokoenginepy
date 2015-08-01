import pytest
from factories import PieceFactory
from hamcrest import assert_that
from sokoenginepy import InvalidPieceIdError, InvalidPiecePlusIdError, Piece


class DescribePiece(object):

    def test_it_is_equality_comparable(self, piece):
        piece2 = PieceFactory()
        piece2.id = piece.id
        piece2.plus_id = piece.plus_id
        piece2.position = piece.position

        assert_that(piece == piece2)

        piece2.id = piece2.id + 1
        assert_that(piece != piece2)
        piece2.id = piece.id

        piece2.plus_id = piece2.plus_id + 1
        assert_that(piece != piece2)
        piece2.plus_id = piece.plus_id

        piece2.position = piece2.position + 1
        assert_that(piece != piece2)
        piece2.position = piece.position

    def test_it_raises_on_invalid_id(self, piece):
        with pytest.raises(InvalidPieceIdError):
            PieceFactory(id=Piece.DEFAULT_ID - 1)
        with pytest.raises(InvalidPieceIdError):
            piece.id = Piece.DEFAULT_ID - 1
        with pytest.raises(InvalidPieceIdError):
            piece.id = None

    def test_it_raises_on_invalid_plus_id(self, piece):
        with pytest.raises(InvalidPiecePlusIdError):
            PieceFactory(plus_id=Piece.DEFAULT_PLUS_ID - 1)
        with pytest.raises(InvalidPiecePlusIdError):
            piece.plus_id = Piece.DEFAULT_PLUS_ID - 1
        with pytest.raises(InvalidPiecePlusIdError):
            piece.plus_id = None
