import numpy as np
from gmpy2 import xmpz
import copy as cp


def bottom(width, height) -> xmpz:
    """
    Generate a bitmask containing 1 for the bottom slot of each column
    :param int width:
    :param int height:
    :return: A bitmask containing 1 for the bottom slot of each column
    """
    if width == 0:
        return 0
    else:
        return bottom(width - 1, height) | xmpz(1) << (width - 1) * (height + 1)


class Position:
    """
    A class storing a Connect 4 position.

    A binary bitboard representation is used to speed up the processes
    """

    WIDTH = 7  # Width of the board
    HEIGHT = 6  # Height of the board
    MIN_SCORE = -(WIDTH * HEIGHT) // 2 + 3
    MAX_SCORE = (WIDTH * HEIGHT + 1) // 2 - 3
    assert WIDTH < 10, "Board's width must be less than 10"
    assert WIDTH * (HEIGHT + 1) <= 64, "Board does not fit a 64bits bitboard"

    # Static bitmaps
    bottom_mask = bottom(WIDTH, HEIGHT)
    board_mask = bottom_mask * ((xmpz(1) << HEIGHT) - 1)

    def __init__(self):
        # Bit representation of stones of the current player
        self.current_position = xmpz()
        self.current_position[64] = 0

        # Bit mask that shows all positions in the board that is not empty
        self.mask = xmpz()
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
    def bottom_mask_col(col) -> xmpz:
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

    @staticmethod
    def compute_winning_position(position, mask) -> xmpz:
        """
        Compute all winning positions for the given position
        :param position: Given player position
        :param mask: Mask of the game
        :return: A bitmask of winning positions
        """

        # Vertical
        v = (position << 1) & (position << 2) & (position << 3)

        # Horizontal
        h = (position << (Position.HEIGHT + 1)) & (position << 2 * (Position.HEIGHT + 1))
        v |= h & (position << 3 * (Position.HEIGHT + 1))
        v |= h & (position >> (Position.HEIGHT + 1))
        h >>= 3 * (Position.HEIGHT + 1)
        v |= h & (position << (Position.HEIGHT + 1))
        v |= h & (position >> 3 * (Position.HEIGHT + 1))

        # Diagonal 1
        h = (position << Position.HEIGHT) & (position << 2 * Position.HEIGHT)
        v |= h & (position << 3 * Position.HEIGHT)
        v |= h & (position >> Position.HEIGHT)
        h >>= 3 * Position.HEIGHT
        v |= h & (position << Position.HEIGHT)
        v |= h & (position >> 3 * Position.HEIGHT)

        # Diagonal 2
        h = (position << (Position.HEIGHT + 2)) & (position << 2 * (Position.HEIGHT + 2))
        v |= h & (position << 3 * (Position.HEIGHT + 2))
        v |= h & (position >> (Position.HEIGHT + 2))
        h >>= 3 * (Position.HEIGHT + 2)
        v |= h & (position << (Position.HEIGHT + 2))
        v |= h & (position >> 3 * (Position.HEIGHT + 2))

        return v & (Position.board_mask ^ mask)

    @staticmethod
    def popcount(m) -> int:
        """
        Counts number of bit set to one in xmpz object
        :param xmpz m: Object to be counted
        """
        c = 0
        while m != 0:
            m &= m - 1
            c += 1
        return c

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
        self.play_bit((self.mask + self.bottom_mask_col(col)) & Position.column_mask(col))

    def play_bit(self, move) -> None:
        """
        Plays a move represented with a bit map
        :param xmpz move: Bit map representing the move
        """
        self.current_position ^= self.mask
        self.mask |= move
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
        return self.winning_position() & self.possible() & self.bottom_mask_col(col)

    def total_moves(self) -> int:
        """
        Returns how many moves played since the beginning of the game
        :return: The number of moves since the beginning of the game
        """
        return self.moves

    def possible(self) -> xmpz:
        """
        :return: A bit map of all possible moves
        """
        return (self.mask + self.bottom_mask) & Position.board_mask

    def opponent_winning_position(self) -> xmpz:
        """
        :return: Return a bitmask of the possible winning positions for the opponent
        """
        # Pass in opponent's position
        return Position.compute_winning_position(self.current_position ^ self.mask, self.mask)

    def winning_position(self) -> xmpz:
        """
        :return: A bitmask of the possible winning position for the current player
        """
        return Position.compute_winning_position(self.current_position, self.mask)

    def can_win_next(self) -> bool:
        """
        :return: True if current player can win next move
        """
        return self.winning_position() & self.possible()

    def possible_non_losing(self) -> xmpz:
        """
        :return: A bit map of all the possible next moves that do not lose in one turn.
        A losing move is a move leaving the possibility for the opponent to win directly.
        """
        assert not self.can_win_next()
        possible_mask = self.possible()
        oppo_win = self.opponent_winning_position()
        forced_moves = possible_mask & oppo_win

        if forced_moves != 0:
            # Check if there is more than 1 forced move
            if forced_moves & (forced_moves - 1) != 0:
                # The opponent has two winning moves
                return 0
            else:
                # Play the single forced moves
                possible_mask = forced_moves
        return possible_mask & ~(oppo_win >> 1)

    def score_move(self, move) -> int:
        """
        Score a possible move
        :param xmpz move: Bit map representation
        :return: The score
        """
        return Position.popcount(self.compute_winning_position(self.current_position | move, self.mask))
