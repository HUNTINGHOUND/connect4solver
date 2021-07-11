from pos import Position
from transposition import Table
import copy as cp
from gmpy2 import xmpz
from sorter import MoveSorter


class Solver:
    """
    Connect 4 solver that contains all relevant algorithm and optimization for solving a connect 4 position
    """

    def __init__(self):
        self.column_order = [0] * Position.WIDTH
        self.node_count = 0

        # Transposition Table
        self.trans_table = Table(8388593)

        # Initialize the column exploration order, starting from center columns.
        # Exploring the minimax tree this way allows us to prune more.
        for i in range(0, Position.WIDTH):
            self.column_order[i] = int(Position.WIDTH // 2 + (1 - 2 * (i % 2)) * (i + 1) // 2)

    def solve(self, p) -> int:
        """
        Solve a position using null-depth window
        :param Position p: The position
        :return:The score of the position
        """
        if p.can_win_next():
            # Check for win in one move
            return (Position.WIDTH * Position.HEIGHT + 1 - p.total_moves()) // 2

        # Define the maximum and minimum score (If we win immediately)
        min_score = -(Position.WIDTH * Position.HEIGHT - p.total_moves()) // 2
        max_score = (Position.WIDTH * Position.HEIGHT + 1 - p.total_moves()) // 2

        while min_score < max_score:
            med = min_score + (max_score - min_score) // 2

            if 0 >= med > min_score // 2:
                med = min_score // 2
            elif 0 <= med < max_score // 2:
                med = max_score // 2

            # Use a null depth window
            r = self.negamax(p, alpha=med, beta=med + 1)
            if r <= med:
                max_score = r
            else:
                min_score = r

        return min_score

    def negamax(self, p, alpha=float('-inf'), beta=float('inf')) -> int:
        """
        Recursively solve a connect 4 position using negamax with alpha beta pruning.
        Meaning of score:

        - 0 for a draw
        - Positive score for forced win for current player. Score is the number of moves before theoretical draw.
        - Negative score for forced lose for current player. Score is the number of moves before theoretical draw.

        Generally, higher/lower the score, quicker the win and bigger the advantage.

        :param Position p: The given position
        :param int alpha: Alpha value for alpha beta pruning
        :param int beta: Beta value for alpha beta pruning
        :return: the score of a position
        """
        assert alpha < beta
        assert not p.can_win_next()
        self.node_count += 1

        next_move = p.possible_non_losing()
        if next_move == 0:
            # If there are no possible moves, we lost next move
            return -(Position.WIDTH * Position.HEIGHT - p.total_moves()) // 2

        # Check for draw
        if p.total_moves() >= Position.WIDTH * Position.HEIGHT - 2:
            return 0

        en = self.trans_table.get(p.key())

        # Set lower bound for score
        min_score = -(Position.WIDTH * Position.HEIGHT - 2 - p.total_moves()) // 2
        if en is not None and not en.is_up:
            min_score = en.val

        if alpha < min_score:
            alpha = min_score
            if alpha >= beta:
                return alpha

        # Set upper bound for score
        max_score = (Position.WIDTH * Position.HEIGHT - 1 - p.total_moves()) // 2
        if en is not None and en.is_up:
            max_score = en.val

        if beta > max_score:
            beta = max_score
            if alpha >= beta:
                return beta

        sorter = MoveSorter()
        for i in range(Position.WIDTH - 1, -1, -1):
            move = next_move & Position.column_mask(self.column_order[i])
            if move != 0:
                sorter.add(move, p.score_move(move))

        tobe_move = sorter.get_next()
        while tobe_move != 0:
            # Deep copy the position and create a new position to negamax
            p2 = cp.deepcopy(p)
            p2.play_bit(tobe_move)
            score = -self.negamax(p2, -beta, -alpha)

            # Alpha beta pruning checks
            if score >= beta:
                # Save lower bound
                self.trans_table.put(p.key(), score, False)
                return score
            if score > alpha:
                alpha = score
            tobe_move = sorter.get_next()

        # save the upperbound of the position
        self.trans_table.put(p.key(), alpha, True)
        return alpha

    def reset(self) -> None:
        """
        Reset the solver
        """
        self.node_count = 0
        self.trans_table.reset()

    def get_node_count(self) -> int:
        """
        Get the node count
        :return: Node count
        """
        return self.node_count
