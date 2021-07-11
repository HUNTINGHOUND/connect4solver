from gmpy2 import xmpz


class Table:
    """
    Transposition Table class for caching repeated position.
    The table will store the most recent positions.
    """

    class Entry:
        """
        Class for storing key and value pair in the transposition table
        """

        def __init__(self):
            """
            Default constructor for the Entry class
            """
            self.key = 0
            self.val = 0

    def __init__(self, size):
        """
        :param int size: Size of the table
        """
        assert size > 0, "Size of the transposition table must be greater than 0"
        self.size = size
        self.T = [self.Entry() for each in range(size)]

    def index(self, key) -> int:
        """
        :param xmpz key: The key that needs to be indexed
        :return: The index
        """
        return key % self.size

    def reset(self) -> None:
        """
        Empty the transpositions table
        """
        self.T = [self.Entry() for each in range(self.size)]

    def put(self, key, val) -> None:
        """
        Store a key value pair
        :param xmpz key: The key
        :param int val: The value
        """
        i = self.index(key)
        self.T[i].key = key
        self.T[i].val = val

    def get(self, key) -> int:
        """
        Get the value of a key
        :param xmpz key: The key
        :return: value of the key, if the key does not exist, 0
        """
        i = self.index(key)
        if self.T[i].key == key:
            return self.T[i].val
        else:
            return 0
