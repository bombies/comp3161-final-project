from flask import request, jsonify, send_file
from app import app
from modules.models.account import AccountType
from modules.routes.auth.auth_route import JWTPayload
from modules.routes.courses.courses_schema import (
    CreateCourseSchema,
    CreateCourseSectionItemSchema,
    CreateCourseSectionSchema,
    GradeAssignmentSchema,
    UpdateCourseSchema,
    CreateAssignmentSchema,
)
from modules.utils.db import db
from modules.utils.route_utils import (
    authenticate,
    create_missing_dirs,
    fetch_session,
    protected_route,
)


@app.route("/courses", methods=["POST"])
@protected_route(roles=[AccountType.Admin])
def create_course():
    body = CreateCourseSchema().load(request.get_json(force=True))
    db_cursor = db.cursor()

    # Find if the course code already exists.
    db_cursor.execute(
        "SELECT * FROM Course WHERE course_code = %s", (body["course_code"],)
    )

    if db_cursor.fetchone():
        return (
            jsonify({"message": "There is already a course with that course code!"}),
            400,
        )

    # Check if the lecturer exists.
    db_cursor.execute(
        "SELECT * FROM LecturerDetails WHERE lecturer_id = %s",
        (body["lecturer_id"],),
    )
    if not db_cursor.fetchone():
        return (
            jsonify({"message": "There is no lecturer with that ID!"}),
            400,
        )

    # Create the course.
    db_cursor.execute(
        "INSERT INTO Course (course_code, course_name, lecturer_id, semester) VALUES (%s, %s, %s, %s)",
        (
            body["course_code"],
            body["course_name"],
            body["lecturer_id"],
            body["semester"],
        ),
    )

    db.commit()
    course_code = db_cursor.lastrowid
    return jsonify({"course_code": course_code}), 201


@app.route("/courses/<string:course_code>", methods=["PATCH"])
@protected_route(roles=[AccountType.Admin])
def update_course(course_code: str):
    body = UpdateCourseSchema().load(request.get_json(force=True))
    db_cursor = db.cursor(dictionary=True)

    # Check if the course exists.
    db_cursor.execute("SELECT * FROM Course WHERE course_code = %s", (course_code,))
    course = db_cursor.fetchone()
    if not course:
        return (
            jsonify({"message": "There is no course with that course code!"}),
            404,
        )

    # Check if the lecturer exists.
    if body.get("lecturer_id"):
        db_cursor.execute(
            "SELECT * FROM Account WHERE id = %s AND account_type = %s",
            (body["lecturer_id"], AccountType.Lecturer.value),
        )
        if not db_cursor.fetchone():
            return (
                jsonify({"message": "There is no lecturer with that ID!"}),
                400,
            )

    # Update the course.
    db_cursor.execute(
        "UPDATE Course SET course_name = %s, lecturer_id = %s, semester = %s WHERE course_code = %s",
        (
            body.get("course_name", course["course_name"]),
            body.get("lecturer_id", course["lecturer_id"]),
            body.get("semester", course["semester"]),
            course_code,
        ),
    )

    db.commit()

    # Fetch current course details
    db_cursor.execute("SELECT * FROM Course WHERE course_code = %s", (course_code,))
    course = db_cursor.fetchone()

    return jsonify(course), 200


@app.route("/courses", methods=["GET"])
@protected_route()
def get_courses():
    db_cursor = db.cursor(dictionary=True)
    db_cursor.execute("SELECT * FROM Course")
    courses = db_cursor.fetchall()
    return jsonify(courses), 200


@app.route("/courses/<string:course_code>", methods=["GET"])
@protected_route()
def get_course(course_code: str):
    db_cursor = db.cursor(dictionary=True)

    # Check if the course exists.
    db_cursor.execute("SELECT * FROM Course WHERE course_code = %s", (course_code,))
    course = db_cursor.fetchone()
    if not course:
        return (
            jsonify({"message": "There is no course with that course code!"}),
            404,
        )

    return jsonify(course), 200


@app.route("/courses/student/<int:student_id>", methods=["GET"])
@protected_route()
def get_courses_for_student(student_id: int):
    session = fetch_session()
    db_cursor = db.cursor(dictionary=True)

    if session["account_type"] == AccountType.Student.name:
        student_details = _fetch_student_details_from_session(session)

        if student_id != student_details["student_id"]:
            return jsonify({"message": "You can only view your own courses!"}), 403

    db_cursor.execute(
        "SELECT * FROM Course WHERE course_code IN (SELECT course_code FROM Enrollment WHERE student_id = %s)",
        (student_id,),
    )

    courses = db_cursor.fetchall()
    if not len(courses):
        return jsonify({"message": "There are no courses for this student!"}), 404
    return jsonify(courses), 200


@app.route("/courses/lecturer/<int:lecturer_id>", methods=["GET"])
@protected_route()
def get_courses_for_lecturer(lecturer_id: int):
    db_cursor = db.cursor(dictionary=True)
    db_cursor.execute("SELECT * FROM Course WHERE lecturer_id = %s", (lecturer_id,))

    courses = db_cursor.fetchall()
    if not len(courses):
        return jsonify({"message": "There are no courses for this lecturer!"}), 404
    return jsonify(courses), 200


@app.route("/courses/register/<string:course_code>", methods=["POST"])
@protected_route([AccountType.Student])
def register_for_course(course_code: str):
    session = fetch_session()
    db_cursor = db.cursor(dictionary=True)

    # Fetch StudentDetails record
    student_details = _fetch_student_details_from_session(session)

    # Check if the course exists.
    db_cursor.execute("SELECT * FROM Course WHERE course_code = %s", (course_code,))
    course = db_cursor.fetchone()
    if not course:
        return (
            jsonify({"message": "There is no course with that course code!"}),
            404,
        )

    # Check if the student is already enrolled in the course.
    db_cursor.execute(
        "SELECT * FROM Enrollment WHERE student_id = %s AND course_code = %s",
        (student_details["student_id"], course_code),
    )
    if db_cursor.fetchone():
        return (
            jsonify({"message": "You are already enrolled in this course!"}),
            400,
        )

    # Register the student for the course.
    db_cursor.execute(
        "INSERT INTO Enrollment (student_id, course_code) VALUES (%s, %s)",
        (student_details["student_id"], course_code),
    )

    db.commit()
    return (
        jsonify(
            {
                "message": "You have been registered for the course!",
                "course_code": course_code,
                "student_id": student_details["student_id"],
            }
        ),
        201,
    )


@app.route("/courses/unregister/<string:course_code>", methods=["DELETE"])
@protected_route([AccountType.Student])
def deregister_from_course(course_code: str):
    session = fetch_session()
    db_cursor = db.cursor(dictionary=True)

    # Fetch StudentDetails record
    student_details = _fetch_student_details_from_session(session)

    # Check if the course exists.
    db_cursor.execute("SELECT * FROM Course WHERE course_code = %s", (course_code,))
    course = db_cursor.fetchone()
    if not course:
        return (
            jsonify({"message": "There is no course with that course code!"}),
            404,
        )

    # Check if the student is enrolled in the course.
    db_cursor.execute(
        "SELECT * FROM Enrollment WHERE student_id = %s AND course_code = %s",
        (student_details["student_id"], course_code),
    )
    if not db_cursor.fetchone():
        return (
            jsonify({"message": "You are not enrolled in this course!"}),
            400,
        )

    # Deregister the student from the course.
    db_cursor.execute(
        "DELETE FROM Enrollment WHERE student_id = %s AND course_code = %s",
        (student_details["student_id"], course_code),
    )

    db.commit()
    return (
        jsonify(
            {
                "message": "You have been deregistered from the course!",
                "student_id": student_details["student_id"],
                **course,
            }
        ),
        200,
    )


@app.route("/courses/<string:course_code>/members", methods=["GET"])
@protected_route()
def get_course_members(course_code: str):
    session = fetch_session()
    db_cursor = db.cursor(dictionary=True)

    if session["account_type"] == AccountType.Student.name:
        # Fetch StudentDetails record
        student_details = _fetch_student_details_from_session(session)

        db_cursor.execute(
            "SELECT * FROM Enrollment WHERE student_id = %s AND course_code = %s",
            (student_details["student_id"], course_code),
        )
        if not db_cursor.fetchone():
            return (
                jsonify({"message": "You can only view members for your courses!"}),
                403,
            )

    db_cursor.execute(
        "SELECT * FROM StudentDetails WHERE student_id IN (SELECT student_id FROM Enrollment WHERE course_code = %s)",
        (course_code,),
    )

    members = db_cursor.fetchall()
    if not len(members):
        return jsonify({"message": "There are no members for this course!"}), 404
    return jsonify(members), 200


@app.route("/courses/<string:course_code>/assignments", methods=["POST", "GET"])
@protected_route()
def handle_assignments(course_code: str):
    if request.method == "POST":
        return create_assignment(course_code)
    else:
        return get_assignments(course_code)


def create_assignment(course_code: str):
    auth_res = authenticate([AccountType.Lecturer])
    if auth_res:
        return auth_res

    body = CreateAssignmentSchema().load(request.get_json(force=True))
    db_cursor = db.cursor(dictionary=True)

    # Check if the course exists.
    db_cursor.execute("SELECT * FROM Course WHERE course_code = %s", (course_code,))
    course = db_cursor.fetchone()
    if not course:
        return (
            jsonify({"message": "There is no course with that course code!"}),
            404,
        )

    # Check if the lecturer is the owner of the course.
    lecturer_details = _fetch_lecturer_details_from_session(fetch_session())
    if course["lecturer_id"] != lecturer_details["lecturer_id"]:
        return (
            jsonify({"message": "You can only create assignments for your courses!"}),
            403,
        )

    # Create the assignment.
    db_cursor.execute(
        "INSERT INTO Assignment (course_code, title, description, deadline, total_marks) VALUES (%s, %s, %s, %s, %s)",
        (
            course_code,
            body["title"],
            body.get("description"),
            body["deadline"],
            body["total_marks"],
        ),
    )

    db.commit()
    assignment_id = db_cursor.lastrowid
    return jsonify({"assignment_id": assignment_id}), 201


def get_assignments(course_code: str):
    db_cursor = db.cursor(dictionary=True)

    # Check if the course exists.
    db_cursor.execute("SELECT * FROM Course WHERE course_code = %s", (course_code,))
    course = db_cursor.fetchone()
    if not course:
        return (
            jsonify({"message": "There is no course with that course code!"}),
            404,
        )

    # If the user is a student, check if they are enrolled in the course.
    session = fetch_session()
    if session["account_type"] == AccountType.Student.name:
        # Fetch StudentDetails record
        student_details = _fetch_student_details_from_session(session)

        db_cursor.execute(
            "SELECT * FROM Enrollment WHERE student_id = %s AND course_code = %s",
            (student_details["student_id"], course_code),
        )
        if not db_cursor.fetchone():
            return (
                jsonify({"message": "You can only view assignments for your courses!"}),
                403,
            )

    db_cursor.execute("SELECT * FROM Assignment WHERE course_code = %s", (course_code,))
    assignments = db_cursor.fetchall()
    if not len(assignments):
        return jsonify({"message": "There are no assignments for this course!"}), 404
    return jsonify(assignments), 200


@app.route("/courses/assignments/<int:assignment_id>/submit", methods=["POST"])
@protected_route([AccountType.Student])
def submit_assignment(assignment_id: int):
    uploaded_file = request.files.get("file")
    if not uploaded_file:
        return jsonify({"message": "No file uploaded!"}), 400

    session = fetch_session()
    db_cursor = db.cursor(dictionary=True)

    # Fetch StudentDetails record
    student_details = _fetch_student_details_from_session(session)

    # Check if the assignment exists.
    db_cursor.execute(
        "SELECT * FROM Assignment WHERE assignment_id = %s", (assignment_id,)
    )
    assignment = db_cursor.fetchone()
    if not assignment:
        return (
            jsonify({"message": "There is no assignment with that ID!"}),
            404,
        )

    # Check if the student is enrolled in the course.
    db_cursor.execute(
        "SELECT * FROM Enrollment WHERE student_id = %s AND course_code = %s",
        (student_details["student_id"], assignment["course_code"]),
    )
    if not db_cursor.fetchone():
        return (
            jsonify({"message": "You are not enrolled in this course!"}),
            400,
        )

    # Check if the assignment has already been submitted.
    db_cursor.execute(
        "SELECT * FROM AssignmentSubmission WHERE assignment_id = %s AND student_id = %s",
        (assignment_id, student_details["student_id"]),
    )
    if db_cursor.fetchone():
        return (
            jsonify({"message": "You have already submitted this assignment!"}),
            400,
        )

    # Save the uploaded file to the data/assignments directory
    file_path = f"data/assignments/{assignment_id}/{student_details['student_id']}_{uploaded_file.filename}"

    create_missing_dirs(file_path)
    uploaded_file.save(file_path)

    # Submit the assignment.
    db_cursor.execute(
        "INSERT INTO AssignmentSubmission (assignment_id, student_id, file_path) VALUES (%s, %s, %s)",
        (
            assignment_id,
            student_details["student_id"],
            file_path,
        ),
    )

    db.commit()

    submission_id = db_cursor.lastrowid
    return (
        jsonify({"message": "Assignment submitted!", "submission_id": submission_id}),
        201,
    )


@app.route("/courses/assignments/<int:assignment_id>/submissions", methods=["GET"])
@protected_route()
def get_submissions_for_assignment(assignment_id: int):
    db_cursor = db.cursor(dictionary=True)

    # Check if the assignment exists.
    db_cursor.execute(
        "SELECT * FROM Assignment WHERE assignment_id = %s", (assignment_id,)
    )
    assignment = db_cursor.fetchone()
    if not assignment:
        return (
            jsonify({"message": "There is no assignment with that ID!"}),
            404,
        )

    # Check if the user is a lecturer and if they teach the course associated with the assignment.
    session = fetch_session()
    if session["account_type"] == AccountType.Lecturer.name:
        # Fetch LecturerDetails record
        lecturer_details = _fetch_lecturer_details_from_session(session)

        db_cursor.execute(
            "SELECT * FROM Course WHERE course_code = %s AND lecturer_id = %s",
            (assignment["course_code"], lecturer_details["lecturer_id"]),
        )

        if not db_cursor.fetchone():
            return (
                jsonify({"message": "You can only view submissions for your courses!"}),
                403,
            )
    elif session["account_type"] == AccountType.Student.name:
        # Fetch StudentDetails record
        student_details = _fetch_student_details_from_session(session)

        db_cursor.execute(
            "SELECT * FROM Enrollment WHERE student_id = %s AND course_code = %s",
            (student_details["student_id"], assignment["course_code"]),
        )

        if not db_cursor.fetchone():
            return (
                jsonify({"message": "You can only view submissions for your courses!"}),
                403,
            )

    query = "SELECT * FROM AssignmentSubmission WHERE assignment_id = %s"
    query_params = (assignment_id,)
    if session["account_type"] == AccountType.Student.name:
        query += " AND student_id = %s"
        query_params += (student_details["student_id"],)

    db_cursor.execute(query, query_params)
    submissions = db_cursor.fetchall()

    if not len(submissions):
        return (
            jsonify({"message": "There are no submissions for this assignment!"}),
            404,
        )
    return jsonify(submissions), 200


@app.route(
    "/courses/assignments/<int:assignment_id>/submissions/<int:submission_id>",
    methods=["GET"],
)
@protected_route()
def get_specific_submission(assignment_id: int, submission_id: int):
    db_cursor = db.cursor(dictionary=True)

    # Check if the assignment exists.
    db_cursor.execute(
        "SELECT * FROM Assignment WHERE assignment_id = %s", (assignment_id,)
    )
    assignment = db_cursor.fetchone()
    if not assignment:
        return (
            jsonify({"message": "There is no assignment with that ID!"}),
            404,
        )

    # Check if the user is a lecturer and if they teach the course associated with the assignment.
    session = fetch_session()
    if session["account_type"] == AccountType.Lecturer.name:
        # Fetch lecturer details
        lecturer_details = _fetch_lecturer_details_from_session(session)

        db_cursor.execute(
            "SELECT * FROM Course WHERE course_code = %s AND lecturer_id = %s",
            (assignment["course_code"], lecturer_details["lecturer_id"]),
        )

        if not db_cursor.fetchone():
            return (
                jsonify({"message": "You can only view submissions for your courses!"}),
                403,
            )
    elif session["account_type"] == AccountType.Student.name:
        # Fetch StudentDetails record
        student_details = _fetch_student_details_from_session(session)

        db_cursor.execute(
            "SELECT * FROM Enrollment WHERE student_id = %s AND course_code = %s",
            (student_details["student_id"], assignment["course_code"]),
        )

        if not db_cursor.fetchone():
            return (
                jsonify({"message": "You can only view submissions for your courses!"}),
                403,
            )

    query = "SELECT * FROM AssignmentSubmission WHERE submission_id = %s AND assignment_id = %s"
    query_params = (submission_id, assignment_id)
    if session["account_type"] == AccountType.Student.name:
        query += " AND student_id = %s"
        query_params += (student_details["student_id"],)

    db_cursor.execute(
        query,
        query_params,
    )

    submission = db_cursor.fetchone()

    if not submission:
        return (
            jsonify(
                {"message": "There is no submission with that ID for this assignment!"}
            ),
            404,
        )
    return jsonify(submission), 200


@app.route(
    "/courses/assignments/<int:assignment_id>/submissions/<int:submission_id>/grade",
    methods=["POST"],
)
@protected_route(roles=[AccountType.Lecturer, AccountType.Admin])
def grade_assignment(assignment_id: int, submission_id: int):
    body = GradeAssignmentSchema().load(request.get_json(force=True))
    db_cursor = db.cursor(dictionary=True)

    # Check if the assignment exists.
    db_cursor.execute(
        "SELECT * FROM Assignment WHERE assignment_id = %s", (assignment_id,)
    )
    assignment = db_cursor.fetchone()
    if not assignment:
        return (
            jsonify({"message": "There is no assignment with that ID!"}),
            404,
        )

    # Check if the submission exists.
    db_cursor.execute(
        "SELECT * FROM AssignmentSubmission WHERE submission_id = %s AND assignment_id = %s",
        (submission_id, assignment_id),
    )
    submission = db_cursor.fetchone()
    if not submission:
        return (
            jsonify(
                {"message": "There is no submission with that ID for this assignment!"}
            ),
            404,
        )

    # Check if the user is a lecturer and if they teach the course associated with the assignment.
    session = fetch_session()
    if session["account_type"] == AccountType.Lecturer.name:
        # Fetch lecturer details
        lecturer_details = _fetch_lecturer_details_from_session(session)

        db_cursor.execute(
            "SELECT * FROM Course WHERE course_code = %s AND lecturer_id = %s",
            (assignment["course_code"], lecturer_details["lecturer_id"]),
        )

        if not db_cursor.fetchone():
            return (
                jsonify(
                    {"message": "You can only grade submissions for your courses!"}
                ),
                403,
            )

    # Grade the assignment.
    db_cursor.execute(
        "UPDATE AssignmentSubmission SET grade = %s WHERE submission_id = %s",
        (body["grade"], submission_id),
    )

    db.commit()

    # Fetch updated submission
    db_cursor.execute(
        "SELECT * FROM AssignmentSubmission WHERE submission_id = %s AND assignment_id = %s",
        (submission_id, assignment_id),
    )
    submission = db_cursor.fetchone()

    return jsonify({**submission, "grade": body["grade"]}), 200


@app.route("/courses/<string:course_code>/sections", methods=["POST", "GET"])
@protected_route()
def handle_course_sections(course_code: str):
    if request.method == "POST":
        return create_course_section(course_code)
    else:
        return get_course_sections(course_code)


def get_course_sections(course_code: str):
    db_cursor = db.cursor(dictionary=True)

    # Check if the course exists.
    db_cursor.execute("SELECT * FROM Course WHERE course_code = %s", (course_code,))
    course = db_cursor.fetchone()
    if not course:
        return (
            jsonify({"message": "There is no course with that course code!"}),
            404,
        )

    # If the user is a student, check if they are enrolled in the course. If the user is a lecturer, check if they teach the course.
    visibility_res = _check_course_visibility(
        fetch_session(),
        course_code,
        err_msgs={
            "student_err": "You can only view sections for your courses!",
            "lecturer_err": "You can only view sections for your courses!",
        },
    )

    if visibility_res:
        return visibility_res

    db_cursor.execute("SELECT * FROM Sections WHERE course_code = %s", (course_code,))
    sections = db_cursor.fetchall()

    if not len(sections):
        return jsonify({"message": "There are no sections for this course!"}), 404
    return jsonify(sections), 200


def create_course_section(course_code: str):
    body = CreateCourseSectionSchema().load(request.get_json(force=True))
    db_cursor = db.cursor(dictionary=True)

    # Check if the course exists.
    db_cursor.execute("SELECT * FROM Course WHERE course_code = %s", (course_code,))
    course = db_cursor.fetchone()
    if not course:
        return (
            jsonify({"message": "There is no course with that course code!"}),
            404,
        )

    session = fetch_session()
    if session["account_type"] == AccountType.Student.name:
        return (
            jsonify({"message": "You can't create sections for courses!"}),
            403,
        )

    # Check if the user is a lecturer and if they teach the course
    if session["account_type"] == AccountType.Lecturer.name:
        # Fetch lecturer details
        lecturer_details = _fetch_lecturer_details_from_session(session)

        if course["lecturer_id"] != lecturer_details["lecturer_id"]:
            return (
                jsonify({"message": "You can only create sections for your courses!"}),
                403,
            )

    # Create the course section.
    db_cursor.execute(
        "INSERT INTO Sections (course_code, section_name) VALUES (%s, %s)",
        (
            course_code,
            body["section_name"],
        ),
    )

    db.commit()
    section_id = db_cursor.lastrowid
    return jsonify({"section_id": section_id}), 201


@app.route(
    "/courses/<string:course_code>/sections/<int:section_id>", methods=["POST", "GET"]
)
@protected_route()
def handle_course_section(course_code: str, section_id: int):
    if request.method == "POST":
        return create_course_section_item(course_code, section_id)
    else:
        return get_course_section(course_code, section_id)


def get_course_section(course_code: str, section_id: int):
    db_cursor = db.cursor(dictionary=True)

    # Check if the course exists.
    db_cursor.execute("SELECT * FROM Course WHERE course_code = %s", (course_code,))
    course = db_cursor.fetchone()
    if not course:
        return (
            jsonify({"message": "There is no course with that course code!"}),
            404,
        )

    # If the user is a student, check if they are enrolled in the course. If the user is a lecturer, check if they teach the course.
    visibility_res = _check_course_visibility(
        fetch_session(),
        course_code,
        err_msgs={
            "student_err": "You can only view sections for your courses!",
            "lecturer_err": "You can only view sections for your courses!",
        },
    )

    if visibility_res:
        return visibility_res

    # Check if the section exists
    db_cursor.execute(
        "SELECT * FROM Sections WHERE course_code = %s AND section_id = %s",
        (course_code, section_id),
    )
    section = db_cursor.fetchone()

    if not section:
        return (
            jsonify({"message": "There is no section with that ID for this course!"}),
            404,
        )

    db_cursor.execute("SELECT * FROM SectionItems WHERE section_id = %s", (section_id,))
    section_items = db_cursor.fetchall()

    if not section:
        return jsonify({"message": "There are no items in this section!"}), 404
    return jsonify({**section, "items": section_items}), 200


def create_course_section_item(course_code: str, section_id: int):
    # Make sure the user isn't a student
    session = fetch_session()
    if session["account_type"] == AccountType.Student.name:
        return (
            jsonify({"message": "You can't create section items for courses!"}),
            403,
        )

    # If they are a lecturer, check if they teach the course
    db_cursor = db.cursor(dictionary=True)
    lecturer_details = _fetch_lecturer_details_from_session(session)

    db_cursor.execute(
        "SELECT * FROM Course WHERE course_code = %s AND lecturer_id = %s",
        (course_code, lecturer_details["lecturer_id"]),
    )

    if not db_cursor.fetchone():
        return (
            jsonify({"message": "You can only create section items for your courses!"}),
            403,
        )

    # Init form data
    form_data = request.form.to_dict()

    # Validate data with schema
    body = CreateCourseSectionItemSchema().load(form_data)

    # If a file is uploaded, save it to the data/course-section-items directory
    file_path = None
    if "file" in request.files:
        uploaded_file = request.files["file"]
        file_path = (
            f"data/course-sections/{course_code}/{section_id}/{uploaded_file.filename}"
        )
        uploaded_file.save(file_path)

    db_cursor = db.cursor(dictionary=True)

    # Check if the section actually exists for the course
    db_cursor.execute(
        "SELECT * FROM Sections WHERE course_code = %s AND section_id = %s",
        (course_code, section_id),
    )
    section = db_cursor.fetchone()

    if not section:
        return (
            jsonify({"message": "There is no section with that ID for this course!"}),
            404,
        )

    # Save the course section item
    db_cursor.execute(
        "INSERT INTO SectionItems (section_id, title, description, deadline, link, file_location) VALUES (%s, %s, %s, %s, %s, %s)",
        (
            section_id,
            body["title"],
            body.get("description"),
            (
                body.get("deadline").strftime("%Y-%m-%dT%H:%M:%S.%f%z")
                if body.get("deadline")
                else None
            ),
            body.get("link"),
            file_path,
        ),
    )

    db.commit()
    section_item_id = db_cursor.lastrowid

    # Fetch created sectiom item
    db_cursor.execute(
        "SELECT * FROM SectionItems WHERE item_id = %s", (section_item_id,)
    )
    section_item = db_cursor.fetchone()

    return jsonify(**section_item), 201


@app.route(
    "/courses/<string:course_code>/sections/<int:section_id>/<int:section_item_id>/file",
    methods=["GET"],
)
@protected_route()
def download_course_section_item_file(
    course_code: str, section_id: int, section_item_id: int
):
    db_cursor = db.cursor(dictionary=True)

    # Check if the course exists.
    db_cursor.execute("SELECT * FROM Course WHERE course_code = %s", (course_code,))
    course = db_cursor.fetchone()
    if not course:
        return (
            jsonify({"message": "There is no course with that course code!"}),
            404,
        )

    # If the user is a student, check if they are enrolled in the course. If the user is a lecturer, check if they teach the course.
    visibility_res = _check_course_visibility(
        fetch_session(),
        course_code,
        err_msgs={
            "student_err": "You can only view sections for your courses!",
            "lecturer_err": "You can only view sections for your courses!",
        },
    )

    if visibility_res:
        return visibility_res

    # Check if the section actually exists for the course
    db_cursor.execute(
        "SELECT * FROM Sections WHERE course_code = %s AND section_id = %s",
        (course_code, section_id),
    )
    section = db_cursor.fetchone()

    if not section:
        return (
            jsonify({"message": "There is no section with that ID for this course!"}),
            404,
        )

    db_cursor.execute(
        "SELECT * FROM SectionItems WHERE item_id = %s AND section_id = %s",
        (section_item_id, section_id),
    )
    section_item = db_cursor.fetchone()

    if not section_item:
        return (
            jsonify(
                {"message": "There is not section item with that ID in that section!"}
            ),
            404,
        )

    # If the section item has a file, return it
    if section_item["file_location"]:
        return send_file(section_item["file_location"], as_attachment=True)
    else:
        return jsonify({"message": "This section item has no file!"}), 404


@app.route(
    "/courses/<string:course_code>/sections/<int:section_id>/<int:section_item_id>/file",
    methods=["GET"],
)
@protected_route()
def download_course_section_item_details(
    course_code: str, section_id: int, section_item_id: int
):
    db_cursor = db.cursor(dictionary=True)

    # Check if the course exists.
    db_cursor.execute("SELECT * FROM Course WHERE course_code = %s", (course_code,))
    course = db_cursor.fetchone()
    if not course:
        return (
            jsonify({"message": "There is no course with that course code!"}),
            404,
        )

    # If the user is a student, check if they are enrolled in the course. If the user is a lecturer, check if they teach the course.
    visibility_res = _check_course_visibility(
        fetch_session(),
        course_code,
        err_msgs={
            "student_err": "You can only view sections for your courses!",
            "lecturer_err": "You can only view sections for your courses!",
        },
    )

    if visibility_res:
        return visibility_res

    # Check if the section actually exists for the course
    db_cursor.execute(
        "SELECT * FROM Sections WHERE course_code = %s AND section_id = %s",
        (course_code, section_id),
    )

    section = db_cursor.fetchone()
    if not section:
        return (
            jsonify({"message": "There is no section with that ID for this course!"}),
            404,
        )

    db_cursor.execute(
        "SELECT * FROM SectionItems WHERE item_id = %s AND section_id = %s",
        (section_item_id, section_id),
    )
    section = db_cursor.fetchone()

    if not len(section):
        return jsonify({"message": "There are no items in this section!"}), 404

    return jsonify(section), 200


def _fetch_student_details(account_id: str, account_type: str | None = None):
    db_cursor = db.cursor(dictionary=True)

    if account_type and account_type != AccountType.Student.name:
        return None
    elif not account_type:
        # Fetch account from database and check account type
        db_cursor.execute(
            "SELECT * FROM Account WHERE id = %s AND account_type = %s",
            (account_id, AccountType.Student.name),
        )
        if not db_cursor.fetchone():
            return None

    db_cursor.execute(
        "SELECT * FROM StudentDetails WHERE account_id = %s", (account_id,)
    )
    return db_cursor.fetchone()


def _fetch_student_details_from_session(session: JWTPayload):
    if session["account_type"] != AccountType.Student.name:
        return None

    db_cursor = db.cursor(dictionary=True)
    db_cursor.execute(
        "SELECT * FROM StudentDetails WHERE account_id = %s", (session["sub"],)
    )
    return db_cursor.fetchone()


def _fetch_lecturer_details(account_id: str, account_type: str | None = None):
    db_cursor = db.cursor(dictionary=True)

    if account_type and account_type != AccountType.Lecturer.name:
        return None
    elif not account_type:
        # Fetch account from database and check account type
        db_cursor.execute(
            "SELECT * FROM Account WHERE id = %s AND account_type = %s",
            (account_id, AccountType.Lecturer.name),
        )
        if not db_cursor.fetchone():
            return None

    db_cursor.execute(
        "SELECT * FROM LecturerDetails WHERE account_id = %s", (account_id,)
    )
    return db_cursor.fetchone()


def _fetch_lecturer_details_from_session(session):
    if session["account_type"] != AccountType.Lecturer.name:
        return None

    db_cursor = db.cursor(dictionary=True)
    db_cursor.execute(
        "SELECT * FROM LecturerDetails WHERE account_id = %s", (session["sub"],)
    )
    return db_cursor.fetchone()


def _check_course_visibility(session, course_code, err_msgs={}):
    # Check if the user is a student and if they are enrolled in the course. If the user is a lecturer, check if they teach the course.
    session = fetch_session()
    if session["account_type"] == AccountType.Student.name:
        db_cursor = db.cursor(dictionary=True)
        student_details = _fetch_student_details_from_session(session)

        db_cursor.execute(
            "SELECT * FROM Enrollment WHERE student_id = %s AND course_code = %s",
            (student_details["student_id"], course_code),
        )
        if not db_cursor.fetchone():
            return (
                jsonify(
                    {
                        "message": err_msgs.get("student_err")
                        or "You can only view your courses!"
                    }
                ),
                403,
            )
    elif session["account_type"] == AccountType.Lecturer.name:
        db_cursor = db.cursor(dictionary=True)
        lecturer_details = _fetch_lecturer_details_from_session(session)

        db_cursor.execute(
            "SELECT * FROM Course WHERE course_code = %s AND lecturer_id = %s",
            (course_code, lecturer_details["lecturer_id"]),
        )

        if not db_cursor.fetchone():
            return (
                jsonify(
                    {
                        "message": err_msgs.get("lecturer_err")
                        or "You can only view your courses!"
                    }
                ),
                403,
            )
