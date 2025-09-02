import csv
import os
from bs4 import BeautifulSoup

def populate_assignments_dict(base_dir='data'):
    """
    Populates the assignments dictionary by reading HTML files from a directory structure.
    Assumes a structure like:
    /data
        /etapa-1
            page1.html
            page2.html
        /etapa-2
            page1.html
    Args:
        base_dir (str): The root directory containing assignment subdirectories.
    Returns:
        dict: The populated assignments_html dictionary.
    """
    assignments = {}
    if not os.path.isdir(base_dir):
        print(f"Error: Directory '{base_dir}' not found. Please create it and add your assignment files.")
        # Create the directory to guide the user
        os.makedirs(os.path.join(base_dir, 'etapa-1'), exist_ok=True)
        os.makedirs(os.path.join(base_dir, 'etapa-2'), exist_ok=True)
        print(f"Created a sample directory structure: '{base_dir}/etapa-1', '{base_dir}/etapa-2'.")
        print("Please add your HTML files there and run the script again.")
        return assignments

    # Iterate through each item in the base directory
    for assignment_name in sorted(os.listdir(base_dir)):
        assignment_path = os.path.join(base_dir, assignment_name)
        # Check if it's a directory
        if os.path.isdir(assignment_path):
            assignments[assignment_name] = []
            # Go through each file in the assignment directory
            for page_file in sorted(os.listdir(assignment_path)):
                if page_file.endswith('.html'):
                    file_path = os.path.join(assignment_path, page_file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            assignments[assignment_name].append(f.read())
                    except Exception as e:
                        print(f"Error reading file {file_path}: {e}")
    return assignments


def extract_grades(assignments_html):
    """
    Extracts student grades from GitHub Classroom HTML pages.

    Args:
        assignments_html (dict): A dictionary where keys are assignment names (e.g., "etapa-1")
                                 and values are lists of HTML content strings for that assignment's pages.

    Returns:
        dict: A dictionary where keys are student names and values are another dictionary
              mapping assignment names to grades.
              e.g., {'student1': {'etapa-1': '100/100', 'etapa-2': '90/100'}}
    """
    student_grades = {}

    # Iterate over each assignment and its corresponding HTML pages
    for assignment_name, html_pages in assignments_html.items():
        # Iterate over each HTML page for the current assignment
        for html_content in html_pages:
            soup = BeautifulSoup(html_content, 'html.parser')

            # Find all list items that contain student information
            student_entries = soup.find_all('div', class_='assignment-repo-list-item')

            for entry in student_entries:
                # Extract student name
                student_name_tag = entry.find('span', class_='h5 mr-2')
                if not student_name_tag:
                    continue
                student_name = student_name_tag.text.strip()

                # Extract grade
                grade = "not submitted"  # Default grade if not submitted or graded
                grade_tag = entry.find('span', class_='Counter--secondary')
                if grade_tag and '/' in grade_tag.text:
                    grade = grade_tag.text.strip()

                # Initialize student record if not already present
                if student_name not in student_grades:
                    student_grades[student_name] = {}

                # Store the grade for the current assignment
                student_grades[student_name][assignment_name] = grade

    return student_grades

def write_grades_to_csv(student_grades, filename="student_grades.csv"):
    """
    Writes the extracted student grades to a CSV file.

    Args:
        student_grades (dict): The dictionary of student grades returned by extract_grades.
        filename (str): The name of the output CSV file.
    """
    # Dynamically generate headers from the data to ensure they match folder names
    all_assignments = set()
    for grades in student_grades.values():
        all_assignments.update(grades.keys())
    
    # Define the headers for the CSV file, sorted alphabetically for consistency
    headers = ['name'] + sorted(list(all_assignments))

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()

        # Write a row for each student
        for student, grades in sorted(student_grades.items()):
            row = {'name': student}
            # Populate grades for each assignment, using 'N/A' if a grade is missing
            for header in headers[1:]:
                 row[header] = grades.get(header, 'N/A')
            writer.writerow(row)
    print(f"Successfully created {filename}")


if __name__ == '__main__':
    # --- Instructions ---
    # 1. Create a directory named 'data' in the same folder as this script.
    # 2. Inside 'data', create a folder for each assignment (e.g., 'etapa-1', 'etapa-2').
    # 3. Place all the HTML page files for an assignment inside its corresponding folder.
    #
    # Example structure:
    # /
    # ├── grade_extractor.py
    # └── data/
    #     ├── etapa-1/
    #     │   ├── page1.html
    #     │   └── page2.html
    #     └── etapa-2/
    #         └── page1.html

    # 1. Populate the assignments dictionary from the /data directory
    assignments = populate_assignments_dict()

    if assignments:
        # 2. Extract the grades from the HTML data
        grades = extract_grades(assignments)

        # 3. Write the extracted grades to a CSV file
        write_grades_to_csv(grades)


