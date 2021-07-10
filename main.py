from pos import Position
from solver import Solver

if __name__ == '__main__':
    pos_seq = "662222576343651642712157"
    pos = Position()
    pos.play_seq(pos_seq)
    is_max = (pos.total_moves() % 2 == 0)
    s = Solver()
    score = s.minimax(pos, is_max)
    print("is_max: ")
    print(is_max)
    print("Score: ")
    print(score)
