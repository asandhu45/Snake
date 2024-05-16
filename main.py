# Import necessary modules
import clr
import random
import sys
import time
import threading
import builtins
from Snake import Segment, Snake  # Import the Segment and Snake classes from the Snake module

# Add reference to System.Drawing and GDIDrawer libraries
clr.AddReference('System.Drawing')
from System.Drawing import Color

clr.AddReference('GDIDrawer')
from GDIDrawer import CDrawer
from GDIDrawer import RandColor

# Define a global lock for thread synchronization
myLock = threading.Lock()
# Initialize global variables
# KeyPressed Code
keyCode = 0
# Game running bool
Running = True
# Game Pause Bool
Pause = False
# CurrentLength of the Snake
currentLength = 0
# Current Score
score = 0
# Start Playing Bool
play = False


# Function to handle the game logic in a separate thread
def GameThread(**kwargs):
    '''
    GameThread(**kwargs)
    :param kwargs:
    :return:
    '''
    global myLock, Running, Pause, keyCode, score, lastKey
    drawerScale = 20

    # Adjust drawer scale if provided in kwargs
    if 'Scale' in kwargs:
        drawerScale = kwargs['Scale']

    # Create a CDrawer object
    cDrawer = CDrawer()

    # Randomly select a starting direction
    keyCode = random.randint(37, 40)

    # Configure the CDrawer
    cDrawer.ContinuousUpdate = False
    cDrawer.Scale = drawerScale
    cDrawer.KeyboardEvent += ButtonDown  # Register the ButtonDown function as the event handler

    # Display initial instructions
    cDrawer.AddText('Press Space To Start! \n Red is Bad || Green is Good +5 \n Press Enter To Pause the Game', 20,
                    RandColor.GetColor())
    cDrawer.Render()

    # Initialize the snake at the center of the screen
    snake = Snake(int(cDrawer.ScaledWidth / 2), int(cDrawer.ScaledHeight / 2))

    grow = 0
    eatFruit = True
    obstacle = 0
    rockList = []

    while True:
        if play:
            if not Pause:
                with myLock:
                    if not Running:
                        break
                time.sleep(0.1)
                grow += 1
                obstacle += 1
                with myLock:
                    snake.Move(keyCode)
                    lastKey = keyCode

                # Check if the game is over
                if snake.GameOver(cDrawer):
                    print('Game Over')
                    with myLock:
                        Running = False

                cDrawer.Clear()
                cDrawer.AddText(f'Score: {score}', 15, RandColor.GetColor())

                snake.Show(cDrawer)

                # Generate and display a fruit
                if eatFruit:
                    fruit = Segment(random.randint(0, cDrawer.ScaledWidth - 1),
                                    random.randint(0, cDrawer.ScaledHeight - 1), Color.Green)
                    eatFruit = False
                fruit.Show(cDrawer)

                # Generate and display obstacles (rocks)
                if obstacle == 20:
                    rock = Segment(random.randint(0, cDrawer.ScaledWidth - 1),
                                   random.randint(0, cDrawer.ScaledHeight - 1), Color.Red)
                    rockList.append(rock)
                    obstacle = 0

                if len(rockList) > 0:
                    for x in rockList:
                        x.Show(cDrawer)
                        if snake.Head()[0].__eq__(x):
                            Running = False

                cDrawer.Render()

                # Handle collision with fruit
                if snake.Head()[0].__eq__(fruit):
                    with myLock:
                        score += 5
                    snake.grow = True
                    eatFruit = True

                # Grow the snake every 10 moves
                if grow == 10:
                    snake.grow = True
                    with myLock:
                        score += 1
                    grow = 0
            else:
                cDrawer.AddText('Game Paused', 20, RandColor.GetColor())

    # Display game over message and final score
    print('Longest Length was : ', end="")
    print(snake.Head()[1])
    cDrawer.Clear()
    cDrawer.AddText(f'Game Ended \n Final Score: {score} \n Longest length : {snake.Head()[1]}', 20, RandColor.GetColor())
    cDrawer.Render()
    print('Game Ended Closing')
    time.sleep(3)
    cDrawer.Close()
    # exit()


# Function to handle keyboard events
def ButtonDown(pressed, keycode, cDrawer):
    global keyCode, myLock, Running, Pause, play, lastKey

    with myLock:
        if pressed:
            # Check if the pressed key is in the direction dictionary
            if int(keycode) in Segment.directionDict:
                oppDir = (-Segment.directionDict[keyCode][0], -Segment.directionDict[keyCode][1])
                for key, value in Segment.directionDict.items():
                    if value == oppDir:
                        oppKey = key
                # Check if the requested direction is not opposite to the current direction
                if int(keycode) != oppKey:
                    keyCode = int(keycode)

            # Toggle pause state when Enter key is pressed
            if int(keycode) == 13:
                with myLock:
                    if play:
                        if not Pause:
                            Pause = True
                        else:
                            Pause = False
            # Start the game when Space key is pressed
            if int(keycode) == 32:
                play = True

            if int(keycode) == 27:
                Running = False


# Function to display the current score
def ScoreBoard():
    global score, Running, Pause

    if not Pause:
        if Running:
            txt = f'Score : {score}'
        else:
            txt = f'Game Ended \n Score : {score} '
    else:
        txt = 'Game Paused'

    drawer = CDrawer(500, 300)
    drawer.ContinuousUpdate = False
    drawer.AddText(txt, 20, RandColor.GetColor())
    drawer.Render()
    time.sleep(0.5)
    drawer.Clear()


# Main entry point of the program
if __name__ == '__main__':
    print('Game Starting')
    print('Red is Bad || Green is +5')
    # Create and start the game thread
    gameThread = threading.Thread(target=GameThread, daemon=True, kwargs={'Scale': 20})
    gameThread.start()

    while True:
        with myLock:
            if not Running:
                time.sleep(3)
                break
        time.sleep(1)
