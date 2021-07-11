import numpy as np
from gmpy2 import xmpz
import copy as cp


class Position:
    """
    A class storing a Connect 4 position.

    A binary bitboard representation is used to speed up the processes
    """

    WIDTH = 7  # Width of the board
    HEIGHT = 6  # Height of the board
    assert WIDTH < 10, "Board's width must be less than 10"
    assert WIDTH * (HEIGHT + 1) <= 64, "Board does not fit a 64bits bitboard"

    def __init__(self):
        # Bit representation of stones of the current player
        self.current_position = xmpz(0)
        self.current_position[64] = 0

        # Bit mask that shows all positions in the board that is not empty
        self.mask = xmpz(0)
        self.mask[64] = 0

        # Number of moves played since the beginning of the game
        self.moves = 0

    @staticmethod
    def top_mask(col) -> xmpz:
        """
        :param int col: The column number indexed 0
        :return: a bitmask containing a single 1 corresponding to the top cell of a given column
        """
        return (xmpz(1) << (Position.HEIGHT - 1)) << col * (Position.HEIGHT + 1)

    @staticmethod
    def bottom_mask(col) -> xmpz:
        """
        :param int col: The column number indexed 0
        :return: a bitmask containing a single 1 corresponding to the bottom cell of a given column
        """
        return xmpz(1) << col * (Position.HEIGHT + 1)

    @staticmethod
    def column_mask(col) -> xmpz:
        """
        :param col: The column number indexed 0
        :return: a bitmask that has 1 on all cells of a given column
        """
        return ((xmpz(1) << Position.HEIGHT) - 1) << col * (Position.HEIGHT + 1)

    @staticmethod
    def alignment(pos) -> bool:
        """
        Test an alignment for current player
        :param c_uint64 pos:
        :return: True if the player has a 4-alignment
        """
        # Horizontal
        m = pos & (pos >> (Position.HEIGHT + 1))
        if m & (m >> 2 * (Position.HEIGHT + 1)) != 0:
            return True

        # Diagonal 1
        m = pos & (pos >> Position.HEIGHT)
        if m & (m >> (2 * Position.HEIGHT)):
            return True

        # Diagonal 2
        m = pos & (pos >> (Position.HEIGHT + 2))
        if m & (m >> (2 * (Position.HEIGHT + 2))):
            return True

        # Vertical
        m = pos & (pos >> 1)
        if m & (m >> 2):
            return True

        return False

    def key(self) -> xmpz:
        """
        :return: A compact representation of a position on WIDTH * (HEIGHT + 1) bits
        """
        return self.current_position + self.mask

    def can_play(self, col) -> bool:
        """
        Check if the given column can be played.
        :return: boolean Value of whether or not given column is playable
        :param int col: The column number indexed 0
        """
        return (self.mask & self.top_mask(col)) == 0

    def play(self, col) -> None:
        """
        Plays a playable column, should not be called on a non-playable column
        :param int col: The column number indexed 0
        """
        # change the current position to opponent, then reflect the change on bit mask
        self.current_position ^= self.mask
        self.mask |= self.mask + self.bottom_mask(col)
        self.moves += 1

    def play_seq(self, seq) -> int:
        """
        Play a sequence of columns. Mainly used to initialize a board.
        Note that processing will stop when:

        - Met invalid character (non digit, or digit >= WIDTH)
        - Playing a column that is already full
        - Playing a column that will win the game
        :param str seq: The sequence of moves corresponding 1-indexed columns
        :return: Number of played moves, caller can compare whether all moves are made by comparing the return value with the length of seq
        """
        for i in range(0, len(seq)):
            col = ord(seq[i]) - ord('1')
            if col < 0 or col >= Position.WIDTH or (not self.can_play(col)) or self.is_winning(col):
                return i  # Invalid move
            self.play(col)

        return len(seq)

    def is_winning(self, col) -> bool:
        """
        Indicates whether the current player wins by playing a given column.
        Should not be called on a non_playable column.
        :param int col: Column number indexed 0
        :return: Whether the given column will cause the current player to win
        """
        pos = cp.deepcopy(self.current_position)
        pos |= (self.mask + self.bottom_mask(col)) & self.column_mask(col)
        return self.alignment(pos);

    def total_moves(self) -> int:
        """
        Returns how many moves played since the beginning of the game
        :return: The number of moves since the beginning of the game
        """
        return self.moves
