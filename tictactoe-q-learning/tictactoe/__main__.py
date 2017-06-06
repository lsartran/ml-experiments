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
import sys
import operator

import tqdm

from tictactoe import Square, Grid, InvalidTicTacToeMove

class RandomPlayer(object):
    def __init__(self, square):
        self.square = square

    #def play(self, grid):
    #    empty_squares = [(i,j) for (i,j),sq in grid.items() if sq == Square.EMPTY]
    #    pos = random.choice(empty_squares)
    #    return pos

    @staticmethod
    def play(grid):
        empty_squares = [(i,j) for (i,j),sq in grid.items() if sq == Square.EMPTY]
        pos = random.choice(empty_squares)
        return pos

    def feedback(self, *args, **kwargs):
        # yeah sure, whatever dude
        pass


class RandomStable(object):
    def player(self, square):
        return RandomPlayer(square)


class LearningStable(object):
    def __init__(self):
        self.quality = {} # (sq, grid: [(action, quality)])
        self.threshold = 0.7

    def player(self, square):
        # XXX beware of different players using the same quality but playing with X instead of O!
        return LearningPlayer(square, self)


class LearningPlayer(object):
    def __init__(self, square, team):
        self.square = square
        self.team = team
        self.quality = team.quality
        self.alpha = 0.01
        self.discount = 1.0
        self.has_played = False

    def play(self, grid):
        self.has_played = True
        s_t = (self.square, int(grid))
        if s_t not in self.quality:
            self.quality[s_t] = {(i,j):0.00 for i in range(3) for j in range(3)}
        if random.random() <= self.team.threshold:
            a_t,q = max(self.quality[s_t].items(),key=operator.itemgetter(1))
            if self.square == Square.NOUGHT and q > 0.0 and q < 1.0 and grid.num_sq == 6:
                pass
        else:
            a_t = RandomPlayer.play(grid)
            #print("Playing with {}".format(str(self.square)))
            #print(str(grid))
            #print(a_t,q)
        self.s_t = s_t
        self.a_t = a_t
        return a_t

    def feedback(self, reward, new_grid):
        if not self.has_played:
            return
        s_tp1 = (self.square, int(new_grid))
        max_Q_s_tp1 = 0.0 if not s_tp1 in self.quality else max(self.quality[s_tp1].values())
        #if max_Q_s_tp1 > 0:
        #    print(self.quality[s_tp1])
        self.quality[self.s_t][self.a_t] += self.alpha * (reward + self.discount * max_Q_s_tp1 - self.quality[self.s_t][self.a_t])

    def fatal(self, reward):
        if self.s_t not in self.quality:
            self.quality[self.s_t] = {(i,j):0.0 for i in range(3) for j in range(3)}
        self.quality[self.s_t][self.a_t] += reward 


def battle(player1, player2):
    assert player1.square == Square.NOUGHT
    assert player2.square == Square.CROSS

    grid = Grid()

    while not grid.full():
        pos = player1.play(grid)
        #print("Player 1",pos)
        try:
            grid[pos] = player1.square
        except InvalidTicTacToeMove:
            player1.fatal(-100)
            return player2.square

        w = grid.winner()
        if w:
            player1.feedback(1.0 if w == player1.square else -1.0, grid)
            player2.feedback(1.0 if w == player2.square else -1.0, grid)
            #print("{} won!".format(str(w)))
            break
        else:
            player1.feedback(0.0, grid)
            player2.feedback(0.0, grid)


        if not grid.full():
            pos = player2.play(grid)
            #print("Player 2",pos)
            try:
                grid[pos] = player2.square
            except InvalidTicTacToeMove:
                player2.fatal(-100)
                return player1.square

            w = grid.winner()
            if w:
                player1.feedback(1.0 if w == player1.square else -1.0, grid)
                player2.feedback(1.0 if w == player2.square else -1.0, grid)
                #print("{} won!".format(str(w)))
                break
            else:
                player1.feedback(0.0, grid)
                player2.feedback(0.0, grid)
    else:
        player1.feedback(-0.0, grid)
        player2.feedback(-0.0, grid)
        w = False

    #print(str(grid))
    return w

if __name__ == '__main__':
    random.seed(42)
    results = {False: 0, 1: 0, 2: 0} # draw, A, B
    num_games = int(sys.argv[1]) if len(sys.argv) >= 2 else 10000
    team_a = LearningStable()
    team_b = RandomStable()
    for _ in tqdm.tqdm(range(num_games)):
        for i in {1,2}:
            player_a = team_a.player(Square.NOUGHT if i == 1 else Square.CROSS)
            player_b = team_a.player(Square.CROSS if i == 1 else Square.NOUGHT)
            if i == 1:
                res = battle(player_a,player_b)
            else:
                res = battle(player_b,player_a)
            if res is False:
                results[False] += 1
            elif res == Square.NOUGHT:
                results[i] += 1
            elif res == Square.CROSS:
                results[3-i] += 1
            else:
                raise Exception

        if _ > 0 and ((_ % 10000) == 0):     
            for k,v in results.items():
                print("{}:\t{}".format(k,0.5*v/_))
            print(len(team_a.quality),len(WIN_CACHE))
    for k,v in results.items():
        print("{}:\t{}".format(k,0.5*v/_))

    print(team_a.quality[(Square.NOUGHT,1-3)])

    team_a.threshold = 1.0
    results = {False: 0, 1: 0, 2: 0} # draw, A, B

    for _ in tqdm.tqdm(range(num_games)):
        for i in {1}:
            player_a = team_a.player(Square.NOUGHT if i == 1 else Square.CROSS)
            player_b = team_a.player(Square.CROSS if i == 1 else Square.NOUGHT)
            if i == 1:
                res = battle(player_a,player_b)
            else:
                res = battle(player_b,player_a)
            if res is False:
                results[False] += 1
            elif res == Square.NOUGHT:
                results[i] += 1
            elif res == Square.CROSS:
                results[3-i] += 1
            else:
                raise Exception

        if _ > 0 and ((_ % 10000) == 0):     
            for k,v in results.items():
                print("{}:\t{}".format(k,1.0*v/10000))
                results = {False: 0, 1: 0, 2: 0} # draw, A, B
            print(len(team_a.quality),len(WIN_CACHE))
    for k,v in results.items():
        print("{}:\t{}".format(k,1.0*v/_))

    print(team_a.quality[(Square.NOUGHT,1-3)])
    print(team_a.quality[(Square.CROSS,1-3+3**8)])
