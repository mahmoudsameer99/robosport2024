#!/usr/bin/env python3
'''Hello to the world from ev3dev.org'''

# Import libraries
from pixycamev3.pixy2 import Pixy2
from ev3dev2.motor import MediumMotor, LargeMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D, MoveSteering
from ev3dev2.sound import Sound
from ev3dev2.sensor.lego import GyroSensor, TouchSensor
from ev3dev2.sensor import INPUT_1, INPUT_4, INPUT_2, INPUT_3
from time import sleep
import time
import scan
from Movement_Methods import Movement
from models import Robot
import models
from attacker import Staker

# Initialize objects
sound = Sound()
my_robot = Robot()
movement = Movement()
staker = Staker()
pixy2 = Pixy2(port=1, i2c_address=0x54)  # Define the Pixy2 camera

# Set up motors and sensors
left_motor = MediumMotor(OUTPUT_B)
right_motor = MediumMotor(OUTPUT_C)
catcher_motor = MediumMotor(OUTPUT_D)  # Motor responsible for catching balls
hiter_motor = LargeMotor(OUTPUT_A)  # Motor responsible for hitting balls
right_motor.polarity = MediumMotor.POLARITY_INVERSED
gyro = GyroSensor(INPUT_4)  # Gyro sensor
touch = TouchSensor(INPUT_3)
gyro.reset()  # Reset gyro readings
driver = MoveSteering(OUTPUT_B, OUTPUT_C, motor_class=MediumMotor)  # Drive base
driver.gyro = gyro  # Gyro sensor for the driver

# Define important integers
wait_duration = 120  # Timer duration in seconds
signature = 1  # Pixy signature

def ball_location(blocks, color):
    """Identify the location of the balls based on their coordinates."""
    ranges = [
        (50, 145, 0, 60, 0),  # Location 0
        (150, 185, 0, 60, 1), # Location 1
        (190, 400, 0, 60, 2), # Location 2
        (50, 140, 65, 140, 3),# Location 3
        (150, 185, 65, 140, 4),# Location 4
        (190, 400, 65, 140, 5) # Location 5
    ]
    ball_locs = []
    for block in blocks:
        x_center = block.x_center
        y_center = block.y_center
        loc = next((index for x_min, x_max, y_min, y_max, index in ranges
                    if x_min <= x_center <= x_max and y_min <= y_center <= y_max), -1)
        ball_locs.append(loc)
    return ball_locs

def side_chooser(ball_locs):
    """Choose and execute actions based on ball locations."""
    unique_ball_locs = set(ball_locs)
    search_functions = {
        0: scan.full_left,
        1: scan.full_middle,
        2: scan.full_right,
        3: scan.middle_of_left,
        4: scan.middle,
        5: scan.middle_of_right
    }
    for ball_loc in unique_ball_locs:
        search_func = search_functions.get(ball_loc)
        if search_func:
            search_func()

def besties(ball_locs):
    """Determine actions when there are orange and purple balls in specific locations."""
    if 4 in ball_locs:
        if 0 in ball_locs:
            models.middle_thin_left()
        elif 2 in ball_locs:
            models.middle_thin_right()
    elif 3 in ball_locs and 1 in ball_locs:
        models.left_thin_middle()
    else:
        side_chooser(ball_locs)

def detect_purple_ball():
    """Detect purple balls using Pixy2 camera."""
    nr_blocks, blocks = pixy2.get_blocks(2, 4)
    purple_ball_locs = []
    for block in blocks:
        purple_ball_locs.extend(ball_location([block], 'purple'))
    return purple_ball_locs

def side_chooser_p(ball_locs):
    """Choose actions based on the detected purple ball locations."""
    unique_ball_locs = set(ball_locs)
    search_functions = {
        0: scan.go_to_pp_ball_full_left,
        1: scan.get_pp_ball_full_middle,
        2: scan.go_to_pp_bal_full_right,
        3: scan.go_home_left_pp_ball,
        4: scan.get_pp_ball_middle,
        5: scan.go_home_right_pp_ball
    }
    for ball_loc in unique_ball_locs:
        search_func = search_functions.get(ball_loc)
        if search_func:
            search_func()

def break_them(ball_locs):
    """Handle interactions with both purple and orange balls."""
    unique_ball_locs = set(ball_locs)
    search_functions = {
        0: scan.full_left_pp_and_o_ball,
        1: scan.full_middle_pp_and_o_ball,
        2: scan.full_right_pp_and_o_ball,
        3: scan.left_pp_and_o_ball,
        4: scan.middle_pp_and_o_ball,
        5: scan.right_pp_and_o_ball
    }
    for ball_loc in unique_ball_locs:
        search_func = search_functions.get(ball_loc)
        if search_func:
            search_func()

def scan_process():
    """Main scanning process for detecting and interacting with balls."""
    start_time = time.time()
    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time > 120:  # Stop after 2 minutes
            print("Scan duration exceeded 2 minutes. Stopping.")
            break

        sleep(3)
        purple_ball_locs = detect_purple_ball()
        print("Purple Ball Locations:", purple_ball_locs)
        
        nr_blocks, blocks = pixy2.get_blocks(signature, 4)
        if nr_blocks > 0:
            ball_locs = ball_location(blocks, 'orange')
            print("Orange Ball Locations:", ball_locs)

            if set(purple_ball_locs) & set(ball_locs):
                break_them(purple_ball_locs)
                print("A purple ball is at the same location as an orange ball.")
            else:
                side_chooser_p(purple_ball_locs)
                if nr_blocks == 1 or nr_blocks >= 3:
                    side_chooser(ball_locs)
                elif nr_blocks == 2:
                    besties(ball_locs)
        else:
            print("No ball detected")

if __name__ == "__main__":
    scan_process()

