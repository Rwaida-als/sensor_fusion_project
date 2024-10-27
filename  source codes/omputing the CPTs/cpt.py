import pandas as pd
import numpy as np
from itertools import product

def compute_cpts():
    # Define the file path
    file_path = '/Users/sarasluiman/Desktop/robot_data.csv'

    try:
        # Attempt to read the CSV with comma delimiter (default)
        df = pd.read_csv(file_path)
        print("Data successfully read with comma delimiter.")
    except Exception as e:
        print(f"Failed to read data with comma delimiter: {e}")
        print("Please check the file format and delimiters.")
        return

    # Print the columns to verify
    print("Columns found in data:", df.columns.tolist())

    # Expected columns
    expected_columns = ['Time', 'Number_of_Bumps', 'Number_of_Doors_Detected',
                        'Distance_to_Wall', 'Right_IR_Reading',
                        'Odometer_X_mm', 'Odometer_Y_mm', 'Odometer_Heading_degrees']

    # Check if all expected columns are present
    missing_columns = [col for col in expected_columns if col not in df.columns]

    if missing_columns:
        print(f"Missing columns: {missing_columns}")
        print("Attempting to set column names manually.")
        # Check if the number of columns matches
        if len(df.columns) == len(expected_columns):
            df.columns = expected_columns
 print("Columns set manually:", df.columns.tolist())
        else:
            print("Number of columns does not match expected. Please verify the data.")   
            return
    else:
        print("All expected columns are present.")
    
    # Ensure required columns are present after setting
    required_columns = ['Time', 'Number_of_Bumps', 'Number_of_Doors_Detected',
                        'Distance_to_Wall', 'Right_IR_Reading']
    for col in required_columns:
        if col not in df.columns:
            print(f"Column '{col}' not found in data. Exiting.")
            return
  # Exclude rows with negative IR readings as 'Invalid'
    initial_row_count = df.shape[0]
    df = df[df['Right_IR_Reading'] >= 0]
    excluded_invalid_ir = initial_row_count - df.shape[0]
    if excluded_invalid_ir > 0:
        print(f"Excluded {excluded_invalid_ir} rows with invalid (negative) IR readings.")
    
    # Exclude rows with missing data in key columns
    initial_row_count = df.shape[0]
    df = df.dropna(subset=['Number_of_Bumps', 'Number_of_Doors_Detected', 'Distance_to_Wall', '$
    excluded_missing = initial_row_count - df.shape[0]
    if excluded_missing > 0:
        print(f"Excluded {excluded_missing} rows with missing data.")
        
    # Create 'Door Detected' as a boolean variable (True/False) 
    df['Door Detected'] = df['Number_of_Doors_Detected'].diff().fillna(0).apply(lambda x: True $
    
    # Categorize Wall Distance
 def categorize_wall_distance(distance):
        if distance < 500:
            return 'Very Close (0-500)'
        elif distance <= 1500: 
            return 'Close (500-1500)'
        elif distance <= 3000:
            return 'Moderate (1500-3000)'
        else:
            return 'Far (>3000)'
    
    df['Wall Distance Category'] = df['Distance_to_Wall'].apply(categorize_wall_distance)
        
    # Categorize IR Values into 'Low', 'Medium', 'High'
    def categorize_ir_value(ir_value):
        if ir_value < 500:
            return 'Low'
elif ir_value <= 1500:
            return 'Medium'
        else:
            return 'High'
        
    df['IR Value Category'] = df['Right_IR_Reading'].apply(categorize_ir_value)
        
    # Compute Overall Probability of Door Detection
    P_Door_Detected = df['Door Detected'].mean()
    print(f"\nP(Door Detected = True): {P_Door_Detected:.2f}")
    
    # Calculate 'Bumps at Time' by finding the difference in 'Number_of_Bumps'
    df['Bumps at Time'] = df['Number_of_Bumps'].diff().fillna(0)
    df['Bumps at Time'] = df['Bumps at Time'].apply(lambda x: int(x) if x >= 0 else 0)
    
    # Categorize 'Bumps at Time' into 0, 1, 2, 'More than 2'
    def categorize_bumps(bumps):
        if bumps == 0:
 return '0'
        elif bumps == 1:
            return '1'   
        elif bumps == 2:
            return '2'
        else:
            return 'More than 2'
    
    df['Bumps Category'] = df['Bumps at Time'].apply(categorize_bumps)
    
    # Define all possible bump categories
    bump_categories = ['0', '1', '2', 'More than 2']
    
    # Ensure 'Bumps Category' is a categorical type with all possible categories
    df['Bumps Category'] = pd.Categorical(df['Bumps Category'], categories=bump_categories, ord$
    
 # Compute CPT for Number of Bumps Category given Door Detected with Laplace smoothing
    cpt_bumps = pd.crosstab(df['Door Detected'], df['Bumps Category'], normalize='index', dropn$
        
    # Apply Laplace smoothing by adding 1 to each count
    cpt_bumps = (cpt_bumps * df.groupby('Door Detected')['Bumps Category'].count().values.resha$
            
    # Ensure all bump categories are present in the CPT
    cpt_bumps = cpt_bumps.reindex(columns=bump_categories, fill_value=1/(df.groupby('Door Detec$
    
    # Normalize rows to ensure they sum to 1
    cpt_bumps = cpt_bumps.div(cpt_bumps.sum(axis=1), axis=0)
    
    # Round probabilities to two decimal places
    cpt_bumps = cpt_bumps.round(2)
    
    print("\nCPT for Number of Bumps Category given Door Detected:")
    print(cpt_bumps)
# Define all possible IR value categories
    ir_categories = ['Low', 'Medium', 'High']
    
    # Define all possible Wall Distance Categories
    wall_distance_categories = ['Very Close (0-500)', 'Close (500-1500)', 'Moderate (1500-3000)$
    
    # Ensure 'IR Value Category' and 'Wall Distance Category' are categorical with all possible$
    df['IR Value Category'] = pd.Categorical(df['IR Value Category'], categories=ir_categories,$
    df['Wall Distance Category'] = pd.Categorical(df['Wall Distance Category'], categories=wall$
    
    # Compute CPT for Wall Distance Category given IR Value Category and Door Detected with Lap$
    cpt_wall_distance = pd.crosstab([df['IR Value Category'], df['Door Detected']],
                                    df['Wall Distance Category'], normalize='index', dropna=Fal$
    
 # Apply Laplace smoothing by adding 1 to each count
    counts_wall = df.groupby(['IR Value Category', 'Door Detected'])['Wall Distance Category'].$
    cpt_wall_distance = (cpt_wall_distance * counts_wall + 1) / (counts_wall + len(wall_distanc$
    
    # Ensure all wall distance categories are present in the CPT
    cpt_wall_distance = cpt_wall_distance.reindex(columns=wall_distance_categories, fill_value=$
    
    # Normalize rows to ensure they sum to 1
    cpt_wall_distance = cpt_wall_distance.div(cpt_wall_distance.sum(axis=1), axis=0)
    
    # Round probabilities to two decimal places
    cpt_wall_distance = cpt_wall_distance.round(2)
    
    print("\nCPT for Wall Distance Category given IR Value Category and Door Detected:")
    print(cpt_wall_distance)
                             # Create table with Bumps Category, Wall Distance Category, Probability of Door Detection
    # Define all possible combinations of Bumps Category and Wall Distance Category
    all_combinations = list(product(bump_categories, wall_distance_categories))
    
    # Create group_counts with all possible combinations
    group_counts = df.groupby(['Bumps Category', 'Wall Distance Category'])['Door Detected'].ag$
    
    # Calculate Probability of Door Detection
    group_counts['Probability of Door Detection'] = group_counts['sum'] / group_counts['count']
    
    # Handle divisions by zero by assigning a default probability of 0.10
    group_counts['Probability of Door Detection'] = np.where(
        group_counts['count'] == 0,
        0.10,
        group_counts['Probability of Door Detection']
    )
                  # Round probabilities to two decimal places
    group_counts['Probability of Door Detection'] = group_counts['Probability of Door Detection$
    
    # Reset index to get columns
    group_counts = group_counts.reset_index()
    
    # Select necessary columns and include 'Number_of_Bumps'
    result_table = group_counts[['Bumps Category', 'Wall Distance Category', 'Probability of Do$
    
    print("\nTable with Bumps Category, Wall Distance Category, Probability of Door Detection:")
    print(result_table)
    
    # Save the CPTs to CSV files   
    cpt_file_path = '/Users/sarasluiman/Desktop/cpt_door_detection.csv'
    result_table.to_csv(cpt_file_path, index=False)  
    print(f"\nCPT saved to {cpt_file_path}")
                                    
    # Optionally, save the other CPTs as well  
    cpt_bumps_file = '/Users/sarasluiman/Desktop/cpt_bumps_given_door_detected.csv'
    cpt_bumps.to_csv(cpt_bumps_file)
 print(f"CPT for Bumps given Door Detected saved to {cpt_bumps_file}")
    
    cpt_wall_distance_file = '/Users/sarasluiman/Desktop/cpt_wall_distance_given_ir_and_door.cs$
    cpt_wall_distance.to_csv(cpt_wall_distance_file)
    print(f"CPT for Wall Distance given IR and Door Detected saved to {cpt_wall_distance_file}")
    
    # Return the computed CPTs and result table
    return cpt_bumps, cpt_wall_distance, result_table
    
# Execute the function
if _name_ == "_main_":
    compute_cpts()