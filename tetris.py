#!/usr/bin/python
# Filename: tetris.py
#
# A game of Tetris
#
# Author; Peter Neyens
# Version: 31-01-2012

import random

class Position:
    '''A postition'''

    def __init__(self, x=0, y=0):
        self.x = int(x)
        self.y = int(y)

    def rotate90(self):
        '''Return the positions when this position is rotated 90 degrees
        clockwise round the origin'''
        comp = complex(self.x, self.y)
        comp *= -1j #rotate 90 degrees
        return Position(comp.real, comp.imag)

    def __repr__(self):
        '''Return a textual representation of this position'''
        return 'P({x},{y})'.format(x=self.x, y=self.y)

    def __eq__(self, other):
        '''Return if this position is equal to the other position'''
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        '''Return the hash of this position'''
        return (self.x * 97) + self.y

class Tetronimo:
    '''A tetronimo that can move left, right and down and rotate and
    has 4 positions'''

    def __init__(self, grid, color):
        if not isinstance(grid, Grid):
            raise ValueError("Parameter grid should be a Grid object")
        self._relPositions = []
        self.position = None
        self.grid = grid
        self.color = color

    def rotate90(self):
        '''Rotate this tetronimo 90 degrees clockwise if possible'''
        rotatedRelPos = []
        for position in self._relPositions:
            relPos = position.rotate90()
            absPos = Position(self.position.x + relPos.x, \
                              self.position.y + relPos.y)
            if self.grid.isOpenPosition(absPos):
                rotatedRelPos.append(relPos)
        if len(rotatedRelPos) == len(self._relPositions):
            self._relPositions = rotatedRelPos

    def positions(self):
        '''Return the position of this tetronimo'''
        positions = []
        for rel in self._relPositions:
            x = self.position.x + rel.x
            y = self.position.y + rel.y
            positions.append(Position(x, y))
        return positions

    def visiblePositions(self):
        '''Return the visible positions of this tetronimo'''
        return [p for p in self.positions() if p <= self.grid.height]

    def moveLeft(self):
        '''Move this tetronimo one position to the left if possible'''
        self._moveDelta(-1, 0)

    def moveRight(self):
        '''Move this tetronimo one position to the right if possible'''
        self._moveDelta(1, 0)

    def moveDown(self):
        '''Move this tetronimo one position down if possible'''
        self._moveDelta(0, -1)

    def canMoveDown(self):
        '''Can this tetronimo move down ?'''
        return self._canMoveDelta(0, -1)

    def canMoveHorizontally(self):
        '''Can this tetronimo move to left or right ?'''
        return self._canMoveDelta(-1, 0) or self._canMoveDelta(1, 0)

    def _moveDelta(self, x, y):
        if self._canMoveDelta(x, y):
            self.position.x += x
            self.position.y += y

    def _canMoveDelta(self, x, y):
        for pos in self.positions():
            if not self.grid.isOpenPosition(Position(pos.x + x, pos.y + y)):
                return False
        return True

class TetronimoL(Tetronimo):

    def __init__(self, grid):
        Tetronimo.__init__(self, grid, Color.ORANGE)
        self._relPositions.append(Position(0, 0));
        self._relPositions.append(Position(1, 0));
        self._relPositions.append(Position(0, 1));
        self._relPositions.append(Position(0, 2));

class TetronimoJ(Tetronimo):

    def __init__(self, grid):
        Tetronimo.__init__(self, grid, Color.BLUE)
        self._relPositions.append(Position(0, 0));
        self._relPositions.append(Position(-1, 0));
        self._relPositions.append(Position(0, 1));
        self._relPositions.append(Position(0, 2));

class TetronimoZ(Tetronimo):

    def __init__(self, grid):
        Tetronimo.__init__(self, grid, Color.GREEN)
        self._relPositions.append(Position(0, 0));
        self._relPositions.append(Position(-1, 1));
        self._relPositions.append(Position(0, 1));
        self._relPositions.append(Position(1, 0));

class TetronimoS(Tetronimo):

    def __init__(self, grid):
        Tetronimo.__init__(self, grid, Color.RED)
        self._relPositions.append(Position(0, 0));
        self._relPositions.append(Position(-1, 0));
        self._relPositions.append(Position(0, 1));
        self._relPositions.append(Position(1, 1));

class TetronimoT(Tetronimo):

    def __init__(self, grid):
        Tetronimo.__init__(self, grid, Color.PURPLE)
        self._relPositions.append(Position(0, 0));
        self._relPositions.append(Position(-1, 0));
        self._relPositions.append(Position(0, 1));
        self._relPositions.append(Position(1, 0));

class TetronimoI(Tetronimo):

    def __init__(self, grid):
        Tetronimo.__init__(self, grid, Color.CYAN)
        self._relPositions.append(Position(0, 0));
        self._relPositions.append(Position(0, -1));
        self._relPositions.append(Position(0, 1));
        self._relPositions.append(Position(0, 2));
        self._vertical = True

    def rotate90(self):
        # if vertical rotate 90 degrees
        Tetronimo.rotate90(self)
        # if horizontal rotate another 180 degrees (270 or -90 degrees in total)
        if not self._vertical:
            Tetronimo.rotate90(self)
            Tetronimo.rotate90(self)
        #switch vertical/horizontal
        self._vertical = not self._vertical

class TetronimoO(Tetronimo):

    def __init__(self, grid):
        Tetronimo.__init__(self, grid, Color.YELLOW)
        self._relPositions.append(Position(0, 0));
        self._relPositions.append(Position(1, 0));
        self._relPositions.append(Position(0, 1));
        self._relPositions.append(Position(1, 1));

    def rotate90(self):
        pass #no rotation

class Grid:
    '''The playing grid'''

    def __init__(self):
        self.width = 10
        self.height = 20
        self._heightWithMargin = self.height + 4;
        self._positions = []

        for x in xrange(self.width):
            self._positions.append([])
            for y in xrange(self._heightWithMargin):
                self._positions[x].append(Color.DEFAULT)

    def getColorAt(self, pos):
        '''Return the color of the given position'''
        if not isinstance(pos, Position):
            raise ValueError("Parameter pos should be a Position object")
        if not self.isValidPosition(pos):
            raise ValueError("The given position is not on the grid")
        return self._positions[pos.x][pos.y]

    def isValidPosition(self, pos):
        '''Lies the given position within the boundries of the grid?'''
        if not isinstance(pos, Position):
            raise ValueError("Parameter pos should be a Position object")
        return (pos.x >= 0 and pos.x < self.width) and \
                (pos.y >= 0 and pos.y < self._heightWithMargin)

    def isOpenPosition(self, pos):
        '''Is the given position valid and open?'''
        if not isinstance(pos, Position):
            raise ValueError("Parameter pos should be a Position object")
        if not self.isValidPosition(pos):
            return False
        return self.getColorAt(pos) == Color.DEFAULT

    def colorPosition(self, pos, color):
        '''Color the given position with the given color'''
        if not isinstance(pos, Position):
            raise ValueError("Parameter pos should be a Position object")
        if self.isValidPosition(pos):
            self._positions[pos.x][pos.y] = color

    def colorTetronimo(self, tetronimo):
        '''Color the tetronimo's positions on this grid'''
        if not isinstance(tetronimo, Tetronimo):
            raise ValueError("Parameter tetronimo should be a Tetronimo object")
        for pos in tetronimo.positions():
            self.colorPosition(pos, tetronimo.color)

    def isLineFull(self, line):
        '''Is the given line full?'''
        for x in xrange(0, self.width):
            if self.isOpenPosition(Position(x, line)):
                return False
        return True

    def hasBlockAtTop(self):
        '''Has a block at the top ? Grid full?'''
        for x in xrange(0, self.width):
            if not self.isOpenPosition(Position(x, self.height-1)):
                return True
        return False

    def removeLine(self, line):
        '''Remove the given line from the grid'''
        if self.isLineFull(line):
            for y in xrange(line, self.height):
                for x in xrange(self.width):
                    if y == self.height-1:
                        self.colorPosition(Position(x,y), Color.DEFAULT)
                    else:
                        color = self.getColorAt(Position(x,y+1))
                        self.colorPosition(Position(x,y), color)

class Color:
    '''Color of tetronimos - enumeration'''
    DEFAULT, CYAN, BLUE, ORANGE, YELLOW, GREEN, PURPLE, RED = range(8)

class Game:
    '''Game object'''

    def __init__(self):
        self.grid = Grid()
        self.droppingTetronimo = self._randomTetronimo()
        self.nextTetronimo = self._randomTetronimo()

    def isEnded(self):
        '''Is this game ended ??'''
        return self.grid.hasBlockAtTop()

    def dropNextTetronimo(self):
        # drop a new tetronimo
        self.droppingTetronimo = self.nextTetronimo
        self.nextTetronimo = self._randomTetronimo()

    def _randomTetronimo(self):
        tetronimos = [TetronimoS(self.grid), TetronimoZ(self.grid),
                      TetronimoL(self.grid), TetronimoO(self.grid),
                      TetronimoI(self.grid), TetronimoJ(self.grid),
                      TetronimoT(self.grid)]
        tetronimo = random.choice(tetronimos)
        tetronimo.position = Position(self.grid.width/2, self.grid.height+1)
        return tetronimo
