CREATE DATABASE University;

USE University;

-- Combining all accounts into a single table with a type to differentiate roles
CREATE TABLE Account (
    account_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    account_type ENUM('Admin', 'Lecturer', 'Student') NOT NULL,
    contact_info VARCHAR(255),
    name VARCHAR(255) NOT NULL
);

-- Details specific to Lecturers
CREATE TABLE LecturerDetails (
    lecturer_id INT AUTO_INCREMENT PRIMARY KEY,
    account_id INT,
    department VARCHAR(255),
    FOREIGN KEY (account_id) REFERENCES Account(account_id)
);

-- Details specific to Students
CREATE TABLE StudentDetails (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    account_id INT,
    gpa DECIMAL(3, 2),
    major VARCHAR(255),
    FOREIGN KEY (account_id) REFERENCES Account(account_id)
);

-- Courses taught by lecturers
CREATE TABLE Course (
    course_code VARCHAR(10) PRIMARY KEY,
    course_name VARCHAR(255) NOT NULL,
    lecturer_id INT,
    semester INT,
    FOREIGN KEY (lecturer_id) REFERENCES LecturerDetails(lecturer_id)
);

-- Sections table 
CREATE TABLE Sections (
    section_id INT AUTO_INCREMENT PRIMARY KEY,
    section_name VARCHAR(255) NOT NULL,
    course_code VARCHAR(10),
    FOREIGN KEY (course_code) REFERENCES Course(course_code)
);

-- SectionItems table 
CREATE TABLE SectionItems (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    section_id INT,
    -- Other Information
    title VARCHAR(255) NOT NULL,
    file_location VARCHAR(255),
    link VARCHAR(255),
    description TEXT,
    deadline DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    -- References
    FOREIGN KEY (section_id) REFERENCES Sections(section_id)
);

-- DiscussionForum table 
CREATE TABLE DiscussionForum (
    forum_id INT AUTO_INCREMENT PRIMARY KEY,
    topic VARCHAR(255) NOT NULL,
    post_time DATETIME NOT NULL,
    creator INT,
    course_code VARCHAR(10),
    FOREIGN KEY (creator) REFERENCES Account(account_id),
    FOREIGN KEY (course_code) REFERENCES Course(course_code)
);

-- DiscussionThread table 
CREATE TABLE DiscussionThread (
    thread_id INT AUTO_INCREMENT PRIMARY KEY,
    replies INT NOT NULL,
    timeStamp DATETIME NOT NULL,
    forum_id INT,
    FOREIGN KEY (forum_id) REFERENCES DiscussionForum(forum_id)
);

-- DiscussionReply table 
CREATE TABLE DiscussionReply (
    reply_id INT AUTO_INCREMENT PRIMARY KEY,
    thread_id INT,
    user_id INT,
    reply_time DATETIME,
    reply_text TEXT,
    FOREIGN KEY (thread_id) REFERENCES DiscussionThread(thread_id),
    FOREIGN KEY (user_id) REFERENCES Account(account_id)
);

-- CalendarEvent table
CREATE TABLE CalendarEvent (
    course_id VARCHAR(10),
    date DATE NOT NULL,
    event_name VARCHAR(255) NOT NULL,
    event_no INT AUTO_INCREMENT PRIMARY KEY,
    FOREIGN KEY (course_id) REFERENCES Course(course_code)
);

-- Assignment table
CREATE TABLE Assignment (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    course_code VARCHAR(10),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    deadline DATETIME,
    total_marks DECIMAL(5, 2),
    FOREIGN KEY (course_code) REFERENCES Course(course_code)
);

-- AssignmentSubmission table 
CREATE TABLE AssignmentSubmission (
    submission_id INT AUTO_INCREMENT PRIMARY KEY,
    assignment_id INT,
    student_id INT,
    submission_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    file_path VARCHAR(255),
    grade DECIMAL(5, 2),
    FOREIGN KEY (assignment_id) REFERENCES Assignment(assignment_id),
    FOREIGN KEY (student_id) REFERENCES StudentDetails(student_id),
    UNIQUE (assignment_id, student_id)
);

CREATE TABLE Enrollment (
    student_id INT,
    course_code VARCHAR(10),
    PRIMARY KEY (student_id, course_code),
    FOREIGN KEY (student_id) REFERENCES StudentDetails(student_id),
    FOREIGN KEY (course_code) REFERENCES Course(course_code)
);