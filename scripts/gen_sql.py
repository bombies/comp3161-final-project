from faker import Faker
import random
from collections import defaultdict

# Initialize Faker generator
fake = Faker()

# Define departments and their potential course themes or titles
department_courses = {
    "Computer Science": [
        "Data Structures",
        "Algorithms",
        "Introduction to Programming",
        "Machine Learning",
        "Computer Networks",
        "Operating Systems",
        "Database Systems",
        "Software Engineering",
        "Human-Computer Interaction",
        "Cybersecurity",
    ],
    "Engineering": [
        "Circuit Analysis",
        "Thermodynamics",
        "Fluid Mechanics",
        "Statics",
        "Dynamics",
        "Material Science",
        "Electrical Systems",
        "Renewable Energy Systems",
        "Control Systems",
        "Signal Processing",
    ],
    "Mathematics": [
        "Calculus",
        "Linear Algebra",
        "Differential Equations",
        "Probability",
        "Statistics",
        "Discrete Mathematics",
        "Real Analysis",
        "Numerical Methods",
        "Complex Analysis",
        "Topology",
    ],
    "Physics": [
        "Mechanics",
        "Electromagnetism",
        "Quantum Physics",
        "Thermodynamics",
        "Optics",
        "Nuclear Physics",
        "Astrophysics",
        "Condensed Matter Physics",
        "Particle Physics",
        "Relativity",
    ],
    "Chemistry": [
        "Organic Chemistry",
        "Inorganic Chemistry",
        "Physical Chemistry",
        "Analytical Chemistry",
        "Biochemistry",
        "Environmental Chemistry",
        "Industrial Chemistry",
        "Polymer Chemistry",
        "Theoretical Chemistry",
        "Medicinal Chemistry",
    ],
    "Biology": [
        "Cell Biology",
        "Genetics",
        "Evolutionary Biology",
        "Ecology",
        "Microbiology",
        "Neuroscience",
        "Plant Biology",
        "Marine Biology",
        "Bioinformatics",
        "Developmental Biology",
    ],
    "English": [
        "English Literature",
        "Creative Writing",
        "Linguistics",
        "American Literature",
        "Comparative Literature",
        "World Literature",
        "Literary Theory",
        "Rhetoric and Composition",
        "Children's Literature",
        "Poetry Writing",
    ],
    "History": [
        "World History",
        "European History",
        "American History",
        "Ancient Civilizations",
        "Medieval Europe",
        "Modern History",
        "Historical Methods",
        "Public History",
        "History of Science",
        "Cultural History",
    ],
    "Psychology": [
        "General Psychology",
        "Abnormal Psychology",
        "Developmental Psychology",
        "Cognitive Psychology",
        "Biopsychology",
        "Social Psychology",
        "Personality Psychology",
        "Clinical Psychology",
        "Forensic Psychology",
        "Industrial-Organizational Psychology",
    ],
    "Economics": [
        "Principles of Economics",
        "Microeconomics",
        "Macroeconomics",
        "Econometrics",
        "International Economics",
        "Development Economics",
        "Behavioral Economics",
        "Environmental Economics",
        "Public Economics",
        "Game Theory",
    ],
}


# Generate a unique course code
def generate_course_code(prefix, number):
    return f"{prefix}{number:03}"


# Map departments to prefixes
department_prefixes = {dept: dept[:2].upper() for dept in department_courses.keys()}

# Generate courses with adjustments - This section remains unchanged
course_examples = []
for _ in range(200):
    dept = random.choice(list(department_courses.keys()))
    prefix = department_prefixes[dept]
    course_number = random.randint(100, 999)
    course_code = generate_course_code(prefix, course_number)
    while any(course[0] == course_code for course in course_examples):
        course_number = random.randint(100, 999)
        course_code = generate_course_code(prefix, course_number)
    course_theme = random.choice(department_courses[dept])
    course_name = course_theme
    semester = random.randint(1, 2)
    lecturer_id = random.randint(1, 50)
    course_examples.append((course_code, course_name, lecturer_id, semester))

# Ensure only unique course codes
course_examples = list(set(course_examples))

# Account creation adjusted for unique contact info
num_lecturers = 50
num_students = 100000  # Total number of students
accounts = []


# Helper function to generate unique contact numbers
def generate_unique_contact(start_sequence, total):
    return [f"{start_sequence}{str(i).zfill(7)}" for i in range(total)]


# Generate unique contact numbers for both lecturers and students
unique_contacts = generate_unique_contact(876, num_lecturers + num_students)

# Initialize a set to track unique emails
unique_emails = set()

# Modify account creation to ensure unique emails
for i in range(1, num_lecturers + 1):  # For lecturers
    email = fake.unique.email()  # Using Faker's unique provider
    while email in unique_emails:  # Ensure email is unique
        email = fake.unique.email()
    unique_emails.add(email)  # Add the new unique email to the set

    dept = random.choice(list(department_courses.keys()))
    accounts.append(
        {
            "account_id": i,
            "email": email,
            "password": fake.password(),
            "account_type": "Lecturer",
            "contact_info": unique_contacts[
                i - 1
            ],  # Adjusted index for unique contacts
            "name": fake.name(),
            "department": dept,
        }
    )

# Adjusted student account creation with GPA
for i in range(num_lecturers + 1, num_lecturers + num_students + 1):
    email = fake.unique.email()
    major = random.choice(list(department_courses.keys()))
    # Generate a random GPA from 0 to 4.33, rounded to 2 decimal places
    gpa = round(random.uniform(0, 4.33), 2)
    accounts.append(
        {
            "account_id": i,
            "email": email,
            "password": fake.password(),
            "account_type": "Student",
            "contact_info": unique_contacts[
                i - 1
            ],  # Assuming unique_contacts is correctly indexed
            "name": fake.name(),
            "major": major,
            "gpa": gpa,  # Include GPA in the account details
        }
    )


num_courses = max(200, num_lecturers)  # Ensure at least as many courses as lecturers

# Initialize lecturer assignments
lecturer_courses = defaultdict(list)

# Assign courses to lecturers ensuring constraints are met
for course_code, course_name, _, _ in course_examples:
    # Randomly select a lecturer to assign
    lecturer_id = random.randint(1, num_lecturers)

    # Ensure no lecturer is assigned more than 5 courses
    while len(lecturer_courses[lecturer_id]) >= 5:
        lecturer_id = random.randint(1, num_lecturers)

    lecturer_courses[lecturer_id].append(course_code)

# Ensure each lecturer teaches at least 1 course
lecturers_without_courses = set(range(1, num_lecturers + 1)) - set(
    lecturer_courses.keys()
)
for lecturer_id in lecturers_without_courses:
    course_to_assign = random.choice(list(lecturer_courses.keys()))
    lecturer_courses[lecturer_id].append(lecturer_courses[course_to_assign].pop())

# Initialize student enrollments
student_enrollments = defaultdict(list)

# List of all course codes
all_course_codes = [code for code, _, _, _ in course_examples]

# Populate student enrollments
student_id = 1  # Start from 1 for enrollment
for acc in accounts:
    if acc["account_type"] == "Student":
        courses_to_enroll = random.sample(all_course_codes, random.randint(3, 6))
        student_enrollments[student_id].extend(courses_to_enroll)
        student_id += 1  # Increment student_id for the next student

# Ensure each course has at least 10 students
course_memberships = defaultdict(list)
for student_id, courses in student_enrollments.items():
    for course_code in courses:
        course_memberships[course_code].append(student_id)

for course_code in all_course_codes:
    while len(course_memberships[course_code]) < 10:
        # Randomly select a student to enroll, ensuring they're not already in the course
        # and do not exceed the 6-course limit
        student_id = random.randint(num_lecturers + 1, num_lecturers + num_students + 1)
        if (
            len(student_enrollments[student_id]) < 6
            and course_code not in student_enrollments[student_id]
        ):
            student_enrollments[student_id].append(course_code)
            course_memberships[course_code].append(student_id)

with open("insert_queries.sql", "w") as f:
    # Insert into Account
    f.write(
        "INSERT INTO Account (account_id, email, password, account_type, contact_info, name) VALUES\n"
    )
    account_values = [
        f"({acc['account_id']}, '{acc['email']}', '{acc['password']}', '{acc['account_type']}', '{acc['contact_info']}', '{acc['name']}')"
        for acc in accounts
    ]
    f.write(",\n".join(account_values))
    f.write(";\n\n")

    # Insert into LecturerDetails
    lecturer_values = [
        f"({lecturer['account_id']}, '{lecturer['department']}')"
        for lecturer in accounts
        if lecturer["account_type"] == "Lecturer"
    ]
    f.write(
        "INSERT INTO LecturerDetails (lecturer_id, department) VALUES\n"
        + ",\n".join(lecturer_values)
        + ";\n\n"
    )

    # Writing student details insertions to SQL file
    f.write("INSERT INTO StudentDetails (student_id, account_id, gpa, major) VALUES\n")

    # Initialize student_id starting from 1
    student_id = 1

    # Generate INSERT statements for StudentDetails
    student_details_values = []
    for acc in accounts:
        if acc["account_type"] == "Student":
            # Use separate student_id and increment it for each student
            student_details_values.append(
                f"({student_id}, {acc['account_id']}, {acc['gpa']}, '{acc['major']}')"
            )
            student_id += 1  # Increment student_id for the next student

    f.write(",\n".join(student_details_values))
    f.write(";\n\n")

    # Insert into Course
    f.write(
        "INSERT INTO Course (course_code, course_name, lecturer_id, semester) VALUES\n"
    )
    course_values = [
        f"('{course[0]}', '{course[1]}', {course[2]}, {course[3]})"
        for course in course_examples
    ]
    f.write(",\n".join(course_values))
    f.write(";\n\n")

    # Writing enrollment insertions to SQL file
    f.write("INSERT INTO Enrollment (student_id, course_code) VALUES\n")

    enrollment_values = [
        f"({student_id}, '{course_code}')"  # Reference updated student_id starting from 1
        for student_id, course_codes in student_enrollments.items()
        for course_code in course_codes
    ]

    f.write(",\n".join(enrollment_values))
    f.write(";\n")


print("SQL insert queries generated and saved to 'insert_queries.sql'")
