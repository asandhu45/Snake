# Import necessary modules
import clr
import random
import sys
import time
import threading
import builtins

# Add reference to GDIDrawer library
clr.AddReference('GDIDrawer')
from GDIDrawer import CDrawer
from GDIDrawer import RandColor

# Define a class named Segment for each segment of the snake
class Segment:
    # Dictionary to map arrow key codes to direction keycodes
    directionDict = {
        # Left Arrow
        37: (-1, 0),
        # Right Arrow
        39: (+1, 0),
        # UP Arrow
        38: (0, -1),
        # Down Arrow
        40: (0, 1)
    }

    # Constructor to initialize a segment with position (x, y), color, and optional parent segment
    def __init__(self, x, y, color, parent=None):
        '''
        CTOR for Segment
        :param x:
        :param y:
        :param color:
        :param parent:
        '''
        self.xPos = x
        self.yPos = y
        self.colr = color
        self.parent = parent

    def __eq__(self, other):
        '''
        Equals Override
        :param other:
        :return:
        '''
        if self.xPos == other.xPos and self.yPos == other.yPos:
            return True
        else:
            return False

    # Method to display the segment on the given CDrawer object
    def Show(self, cDrawer):
        '''
        Show(self, cDrawer)
        :param cDrawer: GdiDrawer
        :return:
        '''
        cDrawer.AddCenteredEllipse(self.xPos, self.yPos, 1, 1, self.colr)
        if self.parent:
            self.parent.Show(cDrawer)

    # Method to move the segment based on the given direction
    def Move(self, direct):
        '''
        Move
        :param direct: direction
        :return:
        '''
        if self.parent:
            x = self.parent.xPos
            y = self.parent.yPos
            self.parent.Move(direct)
            self.xPos = x
            self.yPos = y
        else:
            self.xPos = int((self.directionDict[direct])[0] + self.xPos)
            self.yPos = int((self.directionDict[direct])[1] + self.yPos)

class Snake:
    # Constructor to initialize the snake with a starting position (x, y)
    def __init__(self, x, y):
        self.tail = Segment(x, y, RandColor.GetColor())  # Create the initial segment of the snake
        self.grow = False  # Flag to indicate if the snake should grow

    # Method to display the snake on the given CDrawer object
    def Show(self, cDrawer):
        '''
        Show(self, cDrawer):
        :param cDrawer: GDIDrawer
        :return:
        '''
        self.tail.Show(cDrawer)

    def Move(self, key):
        '''
        Move(self, key):
        :param key: Direction
        :return:
        '''
        if self.grow:
            self.lastPos = (self.tail.xPos, self.tail.yPos)  # Store the position of the last segment
            self.tail = Segment(self.lastPos[0], self.lastPos[1], RandColor.GetColor(), self.tail)  # Add a new segment at the last position
        self.tail.Move(key)  # Move the snake's tail segment
        self.grow = False  # Reset the grow flag

    def GameOver(self, cDrawer):
        '''
        GameOver(self, cDrawer):
        :param cDrawer: GDIDrawer
        :return: if Game is over or not
        '''
        hit = False  # Initialize the hit flag
        snake_head, length = self.Head()  # Get the snake's head and length
        # Check if the snake has hit the boundaries of the CDrawer
        if snake_head.xPos >= cDrawer.ScaledWidth or snake_head.xPos < 0 or snake_head.yPos >= cDrawer.ScaledHeight or snake_head.yPos < 0:
            hit = True
        # Check if the snake has collided with itself (excluding the head)
        body = self.tail
        while body.parent:
            if length > 2 and snake_head == body:
                print('Hit head')
                hit = True
                break
            body = body.parent

        return hit  # Return the hit flag

    def Head(self):
        '''
        Head(self):
        :return: Head part of the snake
        '''
        length = 1  # Initialize the length
        snake = self.tail  # Start with the snake's tail
        while snake.parent:
            length += 1
            snake = snake.parent
        return snake, length  # Return the snake's head and length
