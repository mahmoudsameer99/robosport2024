#!/usr/bin/env python3
'''Hello to the world from ev3dev.org'''

# Import necessary libraries
from pixycamev3.pixy2 import Pixy2
from ev3dev2.motor import MediumMotor, LargeMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D, MoveSteering
from ev3dev2.sound import Sound
import ev3dev2.motor as motor
from ev3dev2.sensor.lego import GyroSensor, TouchSensor
from ev3dev2.sensor import INPUT_1, INPUT_3, INPUT_4
from time import sleep
import time
import random as rd

# Initialize sound for notifications
sound = Sound()

# Import custom modules
from models import Robot
import models
from Movement_Methods import Movement
import scan
from attacker import staker

# Create instances of custom classes
my_robot = Robot()
movement = Movement()
star = staker()

# Set up motors and sensors
left_Motor = MediumMotor(OUTPUT_B)
right_Motor = MediumMotor(OUTPUT_C)
catcher_Motor = MediumMotor(OUTPUT_D)  # Motor for catching balls
hiter_Motor = LargeMotor(OUTPUT_A)  # Motor for hitting balls

# Reverse polarity for the right motor
right_Motor.polarity = MediumMotor.POLARITY_INVERSED

# Initialize Pixy2 camera
pixy2 = Pixy2(port=1, i2c_address=0x54)

# Initialize sensors
gyro = GyroSensor(INPUT_4)  # Gyro sensor for orientation
touch = TouchSensor(INPUT_3)  # Touch sensor for input

# Reset gyro readings
gyro.reset()

# Define drive base using steering
driver = MoveSteering(OUTPUT_B, OUTPUT_C, motor_class=MediumMotor)
driver.gyro = GyroSensor(INPUT_4)  # Set gyro for the driver

# Constants and variables
wait_duration = 120  # Timer duration in seconds
start_time = time.time()  # Start time for timing operations
signtaure = 1  # Identifier used for Pixy2 blocks
ball_loc = int()  # Variable to store ball location index
now = int()  # Variable to store current time
check = True  # Flag for checking conditions
purple_ball = bool  # Variable for detecting purple ball (unused in the script)
s = 0  # State variable for touch sensor handling

# Function to determine ball location based on block coordinates
def ball_location(blocks):
    """
    Determines the ball's location based on the x_center and y_center coordinates of each block.

    Args:
    blocks (list): A list of objects where each object has `x_center` and `y_center` attributes.

    Returns:
    list: A list of integers representing the location index for each block.
    """
    ball_locs = []
    ranges = [
        (50, 145, 0, 60, 0),  # Location 0: x: 50-145, y: 0-60
        (150, 185, 0, 60, 1), # Location 1: x: 150-185, y: 0-60
        (190, 400, 0, 60, 2), # Location 2: x: 190-400, y: 0-60
        (50, 140, 65, 140, 3),# Location 3: x: 50-140, y: 65-140
        (150, 185, 65, 140, 4),# Location 4: x: 150-185, y: 65-140
        (190, 400, 65, 140, 5) # Location 5: x: 190-400, y: 65-140
    ]
    for block in blocks:
        x_center = block.x_center
        y_center = block.y_center
        # Determine the location index based on the block's coordinates
        loc = next((index for x_min, x_max, y_min, y_max, index in ranges
                    if x_min <= x_center <= x_max and y_min <= y_center <= y_max), -1)
        ball_locs.append(loc)  # Add the location index to the list
    return ball_locs

# Function to choose a search direction based on ball locations
def side_chooser(ball_locs):
    """Chooses the direction based on ball locations, avoiding duplicates."""
    unique_ball_locs = set(ball_locs)  # Remove duplicates by converting to a set
    search_functions = {
        0: scan.full_left,        # Location 0 --> Search in the left side game
        1: scan.full_middle,      # Location 1 --> Search in the middle game
        2: scan.full_right,       # Location 2 --> Search in the right side game
        3: scan.middle_of_left,   # Location 3 --> Search in the middle of the left side game
        4: scan.middle,           # Location 4 --> Search in the middle of the middle side game
        5: scan.middle_of_right   # Location 5 --> Search in the middle of the right side game
    }
    for ball_loc in unique_ball_locs:
        search_func = search_functions.get(ball_loc)
        if search_func:
            search_func()  # Call the appropriate search function

# Function to decide the action based on ball locations
def besties(ball_locs):
    """Decides the action based on ball locations."""
    if 4 in ball_locs:
        if 0 in ball_locs:
            models.middle_thin_left()
        elif 2 in ball_locs:
            models.middle_thin_right()
    elif 3 in ball_locs and 1 in ball_locs:
        models.left_thin_middle()
    else:
        side_chooser(ball_locs)

def main():
    """Main loop to detect balls and decide actions."""
    while True:
        sleep(3)  # Wait for 3 seconds
        nr_blocks, blocks = pixy2.get_blocks(signtaure, 4)  # Get blocks from Pixy2
        if nr_blocks > 0:  # Check if any blocks are detected
            x_center = blocks[0].x_center
            y_center = blocks[0].y_center
            print(x_center)  # Print x coordinate of the first block
            print(y_center)  # Print y coordinate of the first block
            ball_locs = ball_location(blocks)  # Determine ball locations

            print(ball_locs)  # Print detected ball locations
            if nr_blocks == 1 or nr_blocks >= 3:
                side_chooser(ball_locs)  # Choose side to search if 1 or 3+ balls are detected
            elif nr_blocks == 2:
                besties(ball_locs)  # Decide action if exactly 2 balls are detected
        else:
            print("no tennis ball detected")  # Print message if no balls are detected

# Main execution starts here
star.normal_atake("home")  # Initial action by the attacker

while True:
    if touch.is_pressed:
        if s == 0:
            scan.ddle()  # Perform some scanning action
            s = 1
        main()  # Run the main loop if the touch sensor is pressed
    else:
        print("touch it")  # Prompt to touch the sensor if not pressed
