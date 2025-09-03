import pandas as pd
import io
import csv
import os
from itertools import zip_longest

# --- Main Data and DataFrame Setup ---

# CSV data provided as a string
csv_data = """name,etapa1,etapa2,etapa3,etapa4
1000neiro,98.80/100,38.78/100,not submitted,
AGuzmannn,not submitted,,,
# ... (rest of your data here) ...
yasmine204,100.00/100,68.14/100,not submitted,
ygabsxw,not submitted,,,
"""

# Read the CSV data into a pandas DataFrame
df = pd.read_csv(io.StringIO(csv_data))
# Fill empty cells (NaN) with empty strings for consistent handling
df = df.fillna('')


# --- Analysis Functions ---

def has_submitted(grade):
    """Check if a grade string represents a valid submission."""
    return isinstance(grade, str) and grade.strip() not in ['', 'not submitted']


def get_performance(grade):
    """
    Calculate the percentage performance from a grade string (e.g., '85/100').
    Returns None if not submitted, or a float percentage.
    Returns -1.0 on a formatting error.
    """
    if not has_submitted(grade):
        return None
    try:
        points, total = map(float, grade.split('/'))
        if total == 0:
            return 0.0
        return (points / total) * 100
    except (ValueError, TypeError):
        return -1.0  # Indicates a malformed grade string


# --- Function to Write Results to CSV ---

def write_analysis_to_csv(analysis_data, filename="analysis_results.csv"):
    """
    Writes the lists of students from the analysis into a single CSV file.
    Each list is treated as a separate column.

    Args:
        analysis_data (dict): Keys are category names, values are lists of students.
        filename (str): Output CSV file name.
    """
    headers = [
        'submitted_stage_1',
        'submitted_stage_2',
        'submitted_stage_3',
        'submitted_stage_4',
        'top_performers (>50%)'
    ]

    # Retrieve and sort each list
    submitted_s1 = sorted(analysis_data.get('submitted_stage_1', []))
    submitted_s2 = sorted(analysis_data.get('submitted_stage_2', []))
    submitted_s3 = sorted(analysis_data.get('submitted_stage_3', []))
    submitted_s4 = sorted(analysis_data.get('submitted_stage_4', []))
    top_performers_list = sorted(analysis_data.get('top_performers', []))

    # Use zip_longest to handle lists of different lengths
    exported_rows = zip_longest(
        submitted_s1,
        submitted_s2,
        submitted_s3,
        submitted_s4,
        top_performers_list,
        fillvalue=''
    )

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            writer.writerows(exported_rows)
        print(f"\nAnalysis successfully saved to {filename}")
    except Exception as e:
        print(f"\nError writing to CSV file: {e}")


# --- Score Validation Functions ---

def is_valid_score(value):
    """
    Returns True if:
    - The value is a string
    - Not empty
    - Does not start with 'not submitted'
    - Contains '/100'
    - Greater than 50
    """
    if not isinstance(value, str):
        return False
    value = value.strip().lower()
    if value == "" or value.startswith("not submitted") or "/100" not in value:
        return False
    try:
        score = float(value.split("/")[0])
        return score > 50
    except ValueError:
        return False


def submitted(value):
    """
    Returns True if the value is a valid submitted grade (>0),
    regardless of whether it's above 50.
    """
    if not isinstance(value, str):
        return False
    value = value.strip().lower()
    if value == "" or value.startswith("not submitted") or "/100" not in value:
        return False
    try:
        score = float(value.split("/")[0])
        return score > 0
    except ValueError:
        return False


def performance_above_50(row):
    """Check if a student has valid scores above 50 in all stages."""
    stages = ["etapa1", "etapa2", "etapa3", "etapa4"]
    return all(is_valid_score(row[stage]) for stage in stages)


# --- Main Execution ---

if __name__ == "__main__":
    # Create folder for results
    os.makedirs("result_page", exist_ok=True)

    # 1. Get lists of students who submitted each stage
    stage1_submitted = df[df["etapa1"].apply(submitted)]
    stage2_submitted = df[df["etapa2"].apply(submitted)]
    stage3_submitted = df[df["etapa3"].apply(submitted)]
    stage4_submitted = df[df["etapa4"].apply(submitted)]

    # 2. Get list of students with performance >50% in all stages
    good_students = df[df.apply(performance_above_50, axis=1)]

    # 3. Print results to console
    print("--- Students who submitted STAGE 1 ---")
    print(sorted(stage1_submitted['name'].tolist()))
    print("\n--- Students who submitted STAGE 2 ---")
    print(sorted(stage2_submitted['name'].tolist()))
    print("\n--- Students who submitted STAGE 3 ---")
    print(sorted(stage3_submitted['name'].tolist()))
    print("\n--- Students who submitted STAGE 4 ---")
    print(sorted(stage4_submitted['name'].tolist()))
    print("\n--- Students with performance greater than 50% in ALL stages ---")
    print(sorted(good_students['name'].tolist()))

    # 4. Write results to CSV
    analysis_results = {
        'submitted_stage_1': stage1_submitted['name'].tolist(),
        'submitted_stage_2': stage2_submitted['name'].tolist(),
        'submitted_stage_3': stage3_submitted['name'].tolist(),
        'submitted_stage_4': stage4_submitted['name'].tolist(),
        'top_performers': good_students['name'].tolist()
    }
    write_analysis_to_csv(analysis_results, filename="result_page/analysis_results.csv")

    # 5. Save individual CSVs for each stage
    stage1_submitted.to_csv("result_page/stage1_submitted.csv", index=False)
    stage2_submitted.to_csv("result_page/stage2_submitted.csv", index=False)
    stage3_submitted.to_csv("result_page/stage3_submitted.csv", index=False)
    stage4_submitted.to_csv("result_page/stage4_submitted.csv", index=False)
    good_students.to_csv("result_page/students_above_50.csv", index=False)

    print("\nCSV files generated in /result_page/")
