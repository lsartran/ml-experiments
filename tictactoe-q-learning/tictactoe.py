"""
Q learning to solve Tic-tac-toe, naive implementation

States: there are 9 spaces in the grid, with 3 possibilities for each (X or O or empty), i.e. 3^9 configurations.
We are not taking into account symmetries, nor the fact that players play alternatively, so not all configurations are reachable through the application of tic-tac-toe rules from an empty board.

Actions: { place a stone at position (i,j) where i is the row number, j the column number | 0 <= i <= 2, 0 <= j <= 2 }

Python 3

TODO:
- smarter representation of the grid
- operate not on the set of grids G, but on the quotient set G / ~ where x~y iff there is an element f of D_4 such that f(x)=y
- make a generic decorator to cache method calls
"""

#from enum import IntEnum
import random

import tqdm

WIN_CACHE = {}

class Square():
    EMPTY = 0
    NOUGHT = 1
    CROSS = -1
    def __str__(self):
        if self == self.__class__.EMPTY:
            return " "
        elif self == self.__class__.NOUGHT:
            return "O"
        elif self == self.__class__.CROSS:
            return "X"

class InvalidTicTacToeMove(Exception):
    pass

class Grid(object):
    def __init__(self, initconf=None):
        # we want to treat an empty square the way we treat one with a nought or a cross
        self.grid = {(i,j): Square.EMPTY for i in range(3) for j in range(3)}
        self.value = 0
        if initconf is not None:
            for (i,j), sq in initconf:
                self[(i,j)] = sq
        assert all((i,j) in self.grid for i in range(3) for j in range(3))

    def __hash__(self):
        return self.value

    def __int__(self):
        return self.value

    def __str__(self):
        return """+-+-+-+
|{}|{}|{}|
+-+-+-+
|{}|{}|{}|
+-+-+-+
|{}|{}|{}|
+-+-+-+""".format(*tuple([str(self[(i,j)]) for i in range(3) for j in range(3) ]))

    def __getitem__(self, key):
        return self.grid.__getitem__(key)

    def __delitem__(self, key):
        raise NotImplementedError
        #return self.grid.__delitem__(key)

    def __contains__(self, key):
        return self.grid.__contains__(key)

    def __setitem__(self, pos, sq):
        if pos not in self:
            raise IndexError
        #if not isinstance(sq, Square):
            #raise TypeError
        if sq == Square.EMPTY:
            raise InvalidTicTacToeMove
        if self[pos] != Square.EMPTY:
            raise InvalidTicTacToeMove
        self.grid[pos] = sq
        (i,j) = pos
        self.value += int(sq) * 3**(3*i+j)

    def items(self):
        return self.grid.items()

    def full(self):
        return not any(sq == Square.EMPTY for _, sq in self.items())

    def _winner(self):
        # FIXME extremely naive, there are better things to do than to test lines and cols and diags like this
        lines = [[(i,j) for j in range(3)] for i in range(3)]
        cols = [[(i,j) for i in range(3)] for j in range(3)]
        diags = [[(i,i) for i in range(3)],[(i,2-i) for i in range(3)]]
        three = lines + cols + diags
        for l in three:
            squares = [self[pos] for pos in l]
            for candidate in {Square.CROSS, Square.NOUGHT}:
                if all(sq == candidate for sq in squares):
                    return candidate
        return False

    def winner(self):
        #return self._winner()
        h = hash(self)
        sgn = (-1 if h < 0 else 1)
        if abs(h) not in WIN_CACHE:
            WIN_CACHE[abs(h)] = sgn * self._winner()
        return WIN_CACHE[abs(h)] * sgn


class RandomPlayer(object):
    def __init__(self, square):
        self.square = square

    def play(self, grid):
        empty_squares = [(i,j) for (i,j),sq in grid.items() if sq == Square.EMPTY]
        pos = random.choice(empty_squares)
        return pos


class RandomStable(object):
    def player(self, square):
        return RandomPlayer(square)


class LearningStable(object);
    def __init__(self):
        self.quality = {}

    def player(self, square):
        # XXX beware of different players using the same quality but playing with X instead of O!
        return LearningPlayer(square, quality)


class LearningPlayer(object):
    def __init__(self, square, quality):
        raise NotImplementedError


def battle(player1, player2):
    grid = Grid()

    while not grid.full():
        pos = player1.play(grid)
        #print("Player 1",pos)
        grid[pos] = Square.NOUGHT

        w = grid.winner()
        if w:
            #print("{} won!".format(str(w)))
            break

        if not grid.full():
            pos = player2.play(grid)
            #print("Player 2",pos)
            grid[pos] = Square.CROSS

            w = grid.winner()
            if w:
                #print("{} won!".format(str(w)))
                break
    else:
        #print("Draw")
        w = False

    #print(str(grid))
    return w

if __name__ == '__main__':
    random.seed(42)
    results = {False: 0, Square.NOUGHT: 0, Square.CROSS: 0}
    num_games = 10000
    s1 = RandomStable()
    s2 = RandomStable()
    for _ in tqdm.tqdm(range(num_games)):
        for (sq1, sq2) in [(Square.NOUGHT,Square.CROSS),(Square.CROSS, Square.NOUGHT)]:
            p1 = s1.player(sq1)
            p2 = s2.player(sq2)
            res = battle(p1,p2)
            if res is False:
                results[False] += 1
            elif res is sq1:
                results[1] += 1
            elif res is sq2:
                results[2] += 1

    for k,v in results.items():
        print("{}:\t{}".format(k,0.5*v/num_games))

