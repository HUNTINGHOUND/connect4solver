from gmpy2 import xmpz
from pos import Position


class MoveSorter:
    """
    This class helps sorting the next moves

    This class uses insertion sort since we are only sorting a small number of moves.
    In addition the move order is already ordered in a semi-sorted way.
    """

    class Entry:
        def __init__(self):
            self.move = xmpz()
            self.score = 0

    def __init__(self):
        self.size = 0
        self.entries = [self.Entry() for each in range(Position.WIDTH)]

    def add(self, move, score) -> None:
        """
        Add a move in the container with its score.
        You cannot add more than Position.WIDTH moves
        :param xmpz move: Bitmap that represents a move
        :param score: Score of the move
        """
        pos = self.size
        self.size += 1
        while (pos != 0) and self.entries[pos - 1].score > score:
            self.entries[pos].move = self.entries[pos - 1].move
            self.entries[pos].score = self.entries[pos - 1].score
            pos -= 1
        self.entries[pos].move = move
        self.entries[pos].score = score

    def get_next(self) -> xmpz:
        """
        Get next move
        :return: Next remaining move with max score and remove it from the container
        """
        if self.size != 0:
            self.size -= 1
            return self.entries[self.size].move
        else:
            return xmpz()
