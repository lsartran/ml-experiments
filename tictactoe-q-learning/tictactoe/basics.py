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
        self.num_sq = 0
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
        #return self.grid.__contains__(key)
        return True

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
        self.num_sq += 1

    def items(self):
        return self.grid.items()

    def full(self):
        #return not any(sq == Square.EMPTY for _, sq in self.items())
        return self.num_sq == 9

    def _winner(self):
        if self.num_sq < 3:
            return False
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
