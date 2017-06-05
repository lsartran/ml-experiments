from tictactoe import Square, Grid

def test_empty_0():
    assert hash(Grid()) == 0

def test_hash_squares():
    assert int(Square.NOUGHT) == 1
    assert int(Square.CROSS) == -1

def test_01_1_1():
    assert hash(Grid([((0,1),Square.NOUGHT)])) == 3

def test_01_2_2():
    assert hash(Grid([((0,1),Square.CROSS)])) == -3

def test_10_1_27():
    assert hash(Grid([((1,0),Square.NOUGHT)])) == 27

def test_10_2_54():
    assert hash(Grid([((1,0),Square.CROSS)])) == -27
