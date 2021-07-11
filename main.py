from pos import Position
from solver import Solver
import time


def get_time():
    return time.time_ns() // 1000


if __name__ == '__main__':
    pos_seq = "763452543756455357732314"

    start = get_time()

    pos = Position()
    pos.play_seq(pos_seq)
    is_max = (pos.total_moves() % 2 == 0)
    s = Solver()
    score = s.solve(pos)

    done = get_time()
    interval = done - start

    print("Score = {}".format(score))
    print("Player 1 starting = {} | Time took = {}μs | Node Count = {}".format(is_max, interval, s.get_node_count()))
