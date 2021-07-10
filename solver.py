from pos import Position
import copy as cp


class Solver:
    """
    Connect 4 solver that contains all relevant algorithm and optimization for solving a connect 4 position
    """

    def __init__(self):
        self.column_order = [0] * Position.WIDTH

        # Initialize the column exploration order, starting from center columns.
        # Exploring the minimax tree this way allows us to prune more.
        for i in range(0, Position.WIDTH):
            self.column_order[i] = int(Position.WIDTH // 2 + (1 - 2 * (i % 2)) * (i + 1) // 2)

    def minimax(self, p, is_max=True, prev_col=-1, alpha=float('-inf'), beta=float('inf')) -> int:
        """
        Recursively solve a connect 4 position using min-max with alpha beta pruning.
        Meaning of score:

        - 0 for a draw
        - Positive score for forced win for player 1. Score is the number of moves before theoretical draw.
        - Negative score for forced win for player 2. Score is the number of moves before theoretical draw.

        Generally, higher/lower the score, quicker the win and bigger the advantage.

        :param Position p: The given position
        :param boolean is_max: Indicate to maximize or minimize
        :param int prev_col: Previously played column indexed 0
        :param int alpha: Alpha value for alpha beta pruning
        :param int beta: Beta value for alpha beta pruning
        :return: the score of a position
        """

        if prev_col != -1:
            # Check if we won
            if p.is_winning(prev_col):
                # Player 1 won
                if p.total_moves() % 2 == 0:
                    # Return the score: 22 - number of moves made by player 1
                    return (Position.HEIGHT * Position.WIDTH) / 2 + 1 - ((p.total_moves() + 1) // 2 + 1)
                # Player 2 won
                else:
                    # Return the score: number of moves made by player 2 - 22
                    return (p.total_moves() // 2 + 1) - ((Position.HEIGHT * Position.WIDTH) / 2 + 1)

            p.play(prev_col)

        # Check if we drew
        if p.total_moves() == Position.WIDTH * Position.HEIGHT:
            return 0

        # We want to maximize aka player 1 turn
        if is_max:
            max_eval = float('-inf')
            for col in range(0, Position.WIDTH):
                if p.can_play(self.column_order[col]):
                    p2 = cp.deepcopy(p)
                    score = self.minimax(p2, False, self.column_order[col], alpha, beta)

                    # Keep track of max score and pruning unnecessary searches
                    if max_eval < score:
                        max_eval = score
                    if alpha < score:
                        alpha = score
                    if beta <= alpha:
                        break

            return max_eval
        # We want to minimize aka player 2 turn
        else:
            min_eval = float('inf')
            for col in range(0, Position.WIDTH):
                if p.can_play(self.column_order[col]):
                    p2 = cp.deepcopy(p)
                    score = self.minimax(p2, True, self.column_order[col], alpha, beta)

                    # Keep track of min score and pruning unnecessary searches
                    if min_eval > score:
                        min_eval = score
                    if beta > score:
                        beta = score
                    if beta <= alpha:
                        break
            return min_eval
