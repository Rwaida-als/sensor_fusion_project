from irobot_edu_sdk.backend.bluetooth import Bluetooth
from irobot_edu_sdk.robots import event, Create3
import time
import asyncio

# Create a robot instance for Create3
robot = Create3(Bluetooth())

# Global variables
number_of_bumps = 0
doors_detected = 0
door_detected_flag = False
door_detected_time = 0
door_cooldown_time = 5  # Cooldown period in seconds to prevent multiple detections of the same door

# Variables to track bump events and delta distance
bump_times = []
delta_distance = False

# Robot speed in mm/s
robot_speed = 100  # Speed for wall-following

# Thresholds and bins
delta_threshold = 20  # Threshold for detecting significant increase in distance
bump_time_threshold = 2  # Seconds between bumps to consider them sequential

# Time tracking
start_time = None

# Constants
INCH_TO_MM = 25.4
DESIRED_DISTANCE_FROM_WALL = 50  # Desired distance in mm (~2 inches)

# Variables for periodic measurement
last_measurement_time = None
measurement_interval = 5  # Measure every 5 seconds

distance_to_wall = None  # Initialize distance_to_wall

# Event handler for right bump detection
@event(robot.when_bumped, [False, True])  # Detect right bump only
async def handle_bump(robot):
    global number_of_bumps, bump_times
    number_of_bumps += 1
    current_time = time.time()
    bump_times.append(current_time)
    # Keep only the last two bump times
    if len(bump_times) > 2:
        bump_times.pop(0)
    # Adjust position when a bump is detected
    print(f"Bump detected on right! Total bumps: {number_of_bumps}")
    await adjust_position_on_bump(robot)

async def monitor_distance():
    global delta_distance, previous_distance, distance_to_wall
    previous_distance = None
    distance_to_wall = None
    while True:
        # Get the current IR proximity sensor reading
        ir_proximity = await robot.get_ir_proximity()
        # Use the right-most sensor; adjust index as necessary
        right_ir = ir_proximity.sensors[-1]  # Adjust index based on your robot

        # Convert sensor reading to distance
        # Assuming higher IR readings mean greater distance from the wall
        # You may need to calibrate this based on your robot's specifications
        distance_to_wall = right_ir  # Replace with actual conversion if available

        # Check for significant increase in distance (possible door)
        if previous_distance is not None and distance_to_wall - previous_distance > delta_threshold:
            delta_distance = True
            print(f"Significant distance increase detected. Delta: {distance_to_wall - previous_distance:.2f} units")
        else:
            delta_distance = False
        previous_distance = distance_to_wall

        await asyncio.sleep(0.1)

async def perform_inference():
    global delta_distance, bump_times, door_detected_flag, door_detected_time, doors_detected
    while True:
        current_time = time.time()

        # Determine B1 and B2
        if len(bump_times) >= 1:
            B1 = 1
            if len(bump_times) >= 2:
                time_diff = bump_times[-1] - bump_times[-2]
                B2 = int(time_diff < bump_time_threshold)
            else:
                B2 = 0
        else:
            B1 = 0
            B2 = 0

        # Delta_Dist_value is already being updated
        Delta_Dist_value = int(delta_distance)

        # Adjusted Door Detection Logic
        if Delta_Dist_value and B1 and B2:
            door_probability = 0.95
        elif Delta_Dist_value and (B1 or B2):
            door_probability = 0.85
        elif Delta_Dist_value:
            door_probability = 0.6
        else:
            door_probability = 0.1

        # Determine if a door has been detected
        if door_probability >= 0.6:
            # Check if enough time has passed since the last door detection
            if (current_time - door_detected_time) > door_cooldown_time:
                doors_detected += 1
                door_detected_flag = True
                door_detected_time = current_time
                print(f"Door detected! Total doors detected: {doors_detected}")
        else:
            door_detected_flag = False

        # Wait before next inference
        await asyncio.sleep(0.1)

async def collect_and_print_data():
    global start_time, number_of_bumps, doors_detected, distance_to_wall
    # Print CSV header
    print("Time,Number of Bumps,Number of Doors Detected,Distance to Wall,Right IR Reading,Odometer X (mm),Odometer Y (mm),Odometer Heading (degrees)")
    while True:
        current_time = time.time() - start_time
        # Get odometer reading
        position = await robot.get_position()
        if hasattr(position, 'x') and hasattr(position, 'y') and hasattr(position, 'heading'):
            position_x = position.x
            position_y = position.y
            heading = position.heading
        else:
            position_x = 0.0
            position_y = 0.0
            heading = 0.0

        # Collect data
        data = [
            f"{current_time:.2f}",
            str(number_of_bumps),
            str(doors_detected),
            f"{distance_to_wall:.2f}" if distance_to_wall is not None else "N/A",
            f"{distance_to_wall:.2f}" if distance_to_wall is not None else "N/A",
            f"{position_x:.2f}",
            f"{position_y:.2f}",
            f"{heading:.2f}"
        ]
        # Print data in CSV format
        print(','.join(data))
        await asyncio.sleep(0.5)

async def wall_following_control():
    global distance_to_wall
    while True:
        # Get the current distance to the wall
        if distance_to_wall is not None:
            # Calculate the error
            error = DESIRED_DISTANCE_FROM_WALL - distance_to_wall
            # Simple proportional controller
            Kp = 0.8  # Adjusted proportional gain for smoother control
            correction = Kp * error
            # Limit correction to reasonable values
            max_correction = 50  # Max correction in mm/s
            correction = max(-max_correction, min(max_correction, correction))
            # Adjust wheel speeds
            left_speed = robot_speed + correction
            right_speed = robot_speed - correction
            # Limit speeds to robot's capabilities
            max_speed = 200  # Max speed in mm/s
            left_speed = max(0, min(max_speed, left_speed))
            right_speed = max(0, min(max_speed, right_speed))
            await robot.set_wheel_speeds(left_speed, right_speed)
        else:
            # If distance_to_wall is not available, keep moving forward
            await robot.set_wheel_speeds(robot_speed, robot_speed)
        await asyncio.sleep(0.1)

async def main_function():
    global door_detected_flag, door_detected_time, start_time, last_measurement_time
    print("\nStarting robot movement.")

    # Start monitoring distance, performing inference, wall following, and collecting data
    asyncio.create_task(monitor_distance())
    asyncio.create_task(perform_inference())
    asyncio.create_task(collect_and_print_data())
    asyncio.create_task(wall_following_control())

    try:
        start_time = time.time()
        last_measurement_time = start_time
        while True:
            current_time = time.time()

            # Every 5 seconds, measure front distance
            if (current_time - last_measurement_time) >= measurement_interval:
                # Measure front distance
                front_distance = await get_front_distance()
                print(f"Front distance to wall: {front_distance:.2f} units")
                # Update last measurement time
                last_measurement_time = current_time

            # Stop after 60 seconds
            if (current_time - start_time) >= 60:
                await robot.set_wheel_speeds(0, 0)  # Stop the robot
                print(f"\nMovement completed.")
                print(f"Total doors detected: {doors_detected}")
                print(f"Final number of bumps detected: {number_of_bumps}")
                break

            await asyncio.sleep(0.1)
    except KeyboardInterrupt:
        await robot.set_wheel_speeds(0, 0)
        print("Program terminated by user.")
    except Exception as e:
        await robot.set_wheel_speeds(0, 0)
        print(f"An error occurred during robot movement: {e}")

async def adjust_position_on_bump(robot):
    # Adjust the robot's position when a bump is detected
    print("Adjusting position due to bump.")
    # Move backward slightly to avoid obstacle
    await robot.move(-30)  # Move backward 30 mm
    # Turn slightly to the left to avoid bumping again
    await robot.turn_left(3)  # Reduced turn angle to 3 degrees
    # Wall-following control will adjust trajectory
    # No need to set wheel speeds here; wall-following will handle it

async def get_front_distance():
    # Function to measure front distance using front IR sensors
    ir_proximity = await robot.get_ir_proximity()
    # Assuming front center sensor; adjust index as necessary
    front_ir = ir_proximity.sensors[2]  # Adjust index based on your robot
    # Convert sensor reading to distance
    front_distance = front_ir  # Replace with actual conversion if available
    return front_distance

# Event handler for when the play button is pressed
@event(robot.when_play)
async def play(robot):
    # Initialize variables
    global start_time
    start_time = time.time()
    # Now, run the main function
    await main_function()

# Start the robot's event loop
robot.play()