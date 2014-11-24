#!/usr/bin/python

import pygame
from pygame.locals import *
from sys import exit
from random import *
from tetris import *

# -----------------------------------------------------------------------------
# TO DO
# -----------------------------------------------------------------------------
# 1)
#------------------------------------------------------------------------------

class GridView:

    def __init__(self, game, screen):
        if not isinstance(game, Game):
            raise ValueError("Parameter game should be a Game object")
        self.grid = game.grid
        self.screen = screen
        self.posToUpdate = []
        self._rect = []
        for x in xrange(self.grid.width):
            self._rect.append([])
            for y in xrange(self.grid.height):
                position = (50 + 30*x, 700 - y*30) # ! move
                size = (25, 25) # ! move
                rect = Rect(position, size)
                self._rect[x].append(rect)

    def _drawPosition(self, pos):
        color = self.grid.getColorAt(pos)
        self._drawPositionWithColor(pos, color)

    def _clearPosition(self, pos):
        self._drawPositionWithColor(pos, Color.DEFAULT)

    def _drawPositionWithColor(self, pos, color):
        if self.grid.isValidPosition(pos) and pos.y < self.grid.height: #margin hack ===> change !!!
            pygame.draw.rect(self.screen, mapColor(color), self._rect[pos.x][pos.y])

    def draw(self):
        '''Draw the grid '''
        self.screen.lock()
        #draw grid
        for x in xrange(game.grid.width):
            for y in xrange(game.grid.height):
                self._drawPosition(Position(x, y))
        #draw tetronimo
        for position in self.tetronimo.positions():
            self._drawPosition(position)
        self.screen.unlock()
        self.update()

    def redraw(self):
        '''Redraw the grid and the given tetronimo'''
        self.screen.lock()
        # clear dirty positions
        for position in self.posToUpdate:
            self._clearPosition(position)
        # redraw tetronimo
        for position in self.tetronimo.visiblePositions():
            self._drawPositionWithColor(position, self.tetronimo.color)
        self.screen.unlock()
        self.update(self.posToUpdate)

    def update(self, posToUpdate = None):
        '''Update the grid after drawing at the given positions'''
        if posToUpdate == None:
            pygame.display.update()
        else:
            dirtyRect = []
            for pos in set(posToUpdate):
                if pos.y < self.grid.height: #margin hack ===> change !!!
                    dirtyRect.append(self._rect[pos.x][pos.y])
            pygame.display.update(dirtyRect)
        self.posToUpdate = []

    def addPosToUpdate(self, pos):
        '''Add positions to be updated when this grid gets redrawn'''
        self.posToUpdate.extend(pos)

    def _tetronimo(self):
        return game.droppingTetronimo

    tetronimo = property(_tetronimo)


def mapColor(color):
    '''Map the given color to a rgb tuple'''
    if color == Color.DEFAULT:
        return (255, 255, 255)
    elif color == Color.CYAN :
        return(0, 255, 255)
    elif color == Color.BLUE :
        return (0, 0, 255)
    elif color == Color.ORANGE :
        return (255, 165, 0)
    elif color == Color.YELLOW :
        return (255, 255, 0)
    elif color == Color.GREEN :
        return (0, 255, 0)
    elif color == Color.PURPLE :
        return (255, 0, 255)
    elif color == Color.RED :
        return (255, 0, 0)

# ------------------------------------------------------------------------------

pygame.init()

game = Game()
screen = pygame.display.set_mode((550, 800), 0, 32)
gridView = GridView(game, screen)
gridView.draw()

clock = pygame.time.Clock()
FPS = 60
framesBeforeDropping = 30
timePlaying = 0

lines = 0

i = 0

while True:

    miliseconds = clock.tick(FPS)
    timePlaying += miliseconds

    tetronimo = game.droppingTetronimo

    redraw = False
    drawTetronimo =  True
    gridView.addPosToUpdate(tetronimo.visiblePositions())

    for event in pygame.event.get():
        if event.type == QUIT:
            exit()
        elif event.type == KEYDOWN:
            if event.key == K_UP:
                tetronimo.rotate90()
                redraw = True
            elif event.key == K_DOWN:
                tetronimo.moveDown()
                redraw = True
            elif event.key == K_LEFT:
                tetronimo.moveLeft()
                redraw = True
            elif event.key == K_RIGHT:
                tetronimo.moveRight()
                redraw = True

    if (i % framesBeforeDropping) == 0:
        tetronimo.moveDown() #speed adjustment
        redraw = True

    # redraw
    if redraw:
        gridView.addPosToUpdate(tetronimo.visiblePositions())
        gridView.redraw()

    if not tetronimo.canMoveDown() and ((i + 1) % framesBeforeDropping) == 0:
        #save the tetronimo on the grid
        game.grid.colorTetronimo(tetronimo)
        drawTetronimo = False

        #check and remove horizontal lines
        linesToCheck = [pos.y for pos in tetronimo.positions()]
        linesToCheck.sort()
        linesToCheck.reverse() #achterwaarts sorteren
        for line in linesToCheck:
            if game.grid.isLineFull(line):
                game.grid.removeLine(line)
                lines += 1
                #levels testing - using framesBeforeDropping    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                if (lines % 5) == 0:
                    framesBeforeDropping -= 1
        gridView.draw()

        # game ended
        if game.isEnded():
            print "The End ..."
            print "You have cleared {lines} lines".format(lines=lines)
            print "You've just played {min} minutes and {sec} seconds of Tetris". \
                format(min= timePlaying/(1000*60), sec = (timePlaying/1000) % 60)
            exit()
        # drop a new tetronimo
        else:
            game.dropNextTetronimo()


    i = (i + 1) % framesBeforeDropping