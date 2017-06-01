"""
Q learning to solve Tic-tac-toe, naive implementation

States: there are 9 spaces in the grid, with 3 possibilities for each (X or O or empty), i.e. 3^9 configurations.
We are not taking into account symmetries, nor the fact that players play alternatively, so not all configurations are reachable through the application of tic-tac-toe rules from an empty board.

Actions: { place a stone at position (i,j) where i is the row number, j the column number | 0 <= i <= 2, 0 <= j <= 2 }

Python 3
"""

from enum import IntEnum

import random

class Square(IntEnum):
    EMPTY = 0
    NOUGHT = 1
    CROSS = 2
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
        if initconf is not None:
            for (i,j), sq in initconf:
                if not ((i >= 0) and (i <= 2) and (j >= 0) and (j <= 2)):
                    raise IndexError
                if not isinstance(sq, Square):
                    raise TypeError
                self.grid[(i,j)] = sq
        assert all((i,j) in self.grid for i in range(3) for j in range(3))

    def __hash__(self):
        return sum(hash(sq)*3**(3*i+j) for (i,j), sq in self.grid.items())

    def __str__(self):
        return """
+-+-+-+
|{}|{}|{}|
+-+-+-+
|{}|{}|{}|
+-+-+-+
|{}|{}|{}|
+-+-+-+""".format(*tuple([str(self[(i,j)]) for i in range(3) for j in range(3) ]))

    def __getitem__(self, key):
        return self.grid.__getitem__(key)

    def __delitem__(self, key):
        return self.grid.__delitem__(key)

    def __contains__(self, key):
        return self.grid.__contains__(key)

    def items(self):
        return self.grid.items()

    def __setitem__(self, pos, sq):
        if pos not in self:
            raise IndexError
        if not isinstance(sq, Square):
            raise TypeError
        if sq == Square.EMPTY:
            raise InvalidTicTacToeMove
        if self[pos] != Square.EMPTY:
            raise InvalidTicTacToeMove
        self.grid[pos] = sq

    def full(self):
        return not any(sq == Square.EMPTY for _, sq in self.items())

class RandomPlayer(object):
    def play(self, grid, sq):
        empty_squares = [(i,j) for (i,j),sq in grid.items() if sq == Square.EMPTY]
        pos = random.choice(empty_squares)
        return pos

def battle(player1, player2):
    grid = Grid()

    while not grid.full():
        pos = player1.play(grid, Square.NOUGHT)
        print("Player 1",pos)
        grid[pos] = Square.NOUGHT

        if not grid.full():
            pos = player2.play(grid, Square.CROSS)
            print("Player 2",pos)
            grid[pos] = Square.CROSS

    print(str(grid))

random.seed(42)
p1 = RandomPlayer()
p2 = RandomPlayer()
battle(p1,p2)

