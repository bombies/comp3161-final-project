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
    section_name VARCHAR(255) NOT NULL
);

-- SectionItems table
CREATE TABLE SectionItems (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    item_name VARCHAR(255) NOT NULL,
    section_id INT,
    FOREIGN KEY (section_id) REFERENCES Sections(section_id)
);

-- DiscussionForum table
CREATE TABLE DiscussionForum (
    forum_id INT AUTO_INCREMENT PRIMARY KEY,
    topic VARCHAR(255) NOT NULL,
    post_time DATETIME NOT NULL,
    creator INT,
    FOREIGN KEY (creator) REFERENCES Account(account_id)
);

-- DiscussionThread table
CREATE TABLE DiscussionThread (
    thread_id INT AUTO_INCREMENT PRIMARY KEY,
    replies INT NOT NULL,
    timeStamp DATETIME NOT NULL,
    forum_id INT,
    FOREIGN KEY (forum_id) REFERENCES DiscussionForum(forum_id)
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
    Assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    Assignment_grade DECIMAL(5, 2)
);

CREATE TABLE Enrollment (
    student_id INT,
    course_code VARCHAR(10),
    PRIMARY KEY (student_id, course_code),
    FOREIGN KEY (student_id) REFERENCES StudentDetails(student_id),
    FOREIGN KEY (course_code) REFERENCES Course(course_code)
);
