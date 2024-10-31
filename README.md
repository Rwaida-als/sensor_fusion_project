
# Sensor Fusion Project - iCreate 3 Robot

This project implements a **sensor fusion module** using a **Bayesian Network** on the iCreate 3 robot. 
The robot can:
- Detect if it has **passed a door 10 cm ago**.
- Calculate the **distance from the wall** as a probability distribution.
- Learn **CPTs (Conditional Probability Tables)** from sensor data.

## Project Structure
```
sensor_fusion_project/
│
├── cpt.py               # Computes CPTs from collected data
├── measurement.py       # Collects sensor readings from the robot
├── sensor.py            # Helper functions including belief() API
├── robot_data.csv       # Raw data collected during robot runs
├── robot_readings.csv   # Processed sensor readings
├── cpt_door_detection.csv                # CPT for door detection
├── cpt_bumps_given_door_detected.csv     # CPT for bumps given door detected
├── cpt_wall_distance_given_ir_and_door.csv  # CPT for wall distance based on IR and door
├── requirements.txt     # (If dependencies are needed)
└── README.md            # Project documentation
```

## How to Use the Project

1. **Clone the Repository**
Open your terminal and run:
```bash
git clone https://github.com/Rwaida-als/sensor_fusion_project.git
cd sensor_fusion_project
```

2. **Install Dependencies**
If you need specific packages, add them to `requirements.txt` and install them:
```bash
pip install -r requirements.txt
```

3. **Collect Sensor Data**
Use the following command to run the robot and collect data:
```bash
python measurement.py
```
The data will be saved in `robot_data.csv` for processing.

4. **Generate CPTs**
After collecting the data, run:
```bash
python cpt.py
```
This script will generate the CPTs and save them in the corresponding CSV files (e.g., `cpt_door_detection.csv`).

5. **Compute Belief Map**
The `belief()` function in `sensor.py` computes the belief map based on sensor readings. Here’s how to use it:
```python
from sensor import belief

# Example sonar readings and configuration
sonar_readings = [1.2, 1.5, 1.1]
inner_config = {"angle": 30, "speed": 0.5}

# Compute belief map
belief_map = belief(sonar_readings, inner_config)
print(belief_map)
```

6. **View Results**
- **CPT files** can be opened in Excel or any CSV viewer for analysis.
- **Belief maps** can also be exported as CSV for visualization.

## Project Website
Visit the website: [Sensor Fusion Project](https://rwaida-als.github.io/sensor_fusion_project/)

## Results and Outputs
- **CSV Files**:
  - `cpt_door_detection.csv`: Probability of detecting a door.
  - `cpt_bumps_given_door_detected.csv`: Probability of bumps given door detection.
  - `cpt_wall_distance_given_ir_and_door.csv`: Probability distribution of distance from the wall.
