Placement Cell Project

The Placement Cell Project is designed to streamline student registrations, job postings, and recruiter interactions. This platform allows students to register for job opportunities, while Placement Cell (P-Cell) coordinators shortlist candidates and send that list to the respective companies.

Setup Instructions

Create a Virtual Environment :
Before running the Flask application, it's essential to create a virtual environment. Flask requires a virtual environment for proper functionality.

Database Configuration :
In the database.py file, you must enter your database password. 
Create a database named- ""Create the SQL tables in SQL-workbench. Afterward, you can insert some sample data into the tables.

SQL Schema :

The following SQL tables are required for the Placement Cell System:

1. Companies Table :
   
This table stores information about the companies that are recruiting.

sql :

CREATE TABLE company (
    company_name VARCHAR(28) PRIMARY KEY, 
    logo_url VARCHAR(2048) NOT NULL, 
    password VARCHAR(16) NOT NULL, 
    company_email VARCHAR(56) NOT NULL, 
    linkedin_url VARCHAR(2048)
);

2. Job Openings Table :
   
This table contains information about job openings available for students.

sql :

CREATE TABLE job_opening (
    job_id INT PRIMARY KEY AUTO_INCREMENT, 
    job_title VARCHAR(30) NOT NULL, 
    opening_status VARCHAR(10) NOT NULL, 
    job_type VARCHAR(25) NOT NULL, 
    salary INT NOT NULL, 
    benefits VARCHAR(200) NOT NULL, 
    location VARCHAR(40) NOT NULL, 
    interview_date DATE NOT NULL, 
    company_name VARCHAR(28) NOT NULL,  
    FOREIGN KEY(company_name) REFERENCES company(company_name), 
    cgpa DECIMAL(4, 2) NOT NULL
);

3. Students Table :
   
This table stores student information for job applications.

sql :

CREATE TABLE student (
    rollnumber VARCHAR(15) PRIMARY KEY, 
    firstname VARCHAR(28) NOT NULL, 
    lastname VARCHAR(28) NOT NULL, 
    year_of_grad INT NOT NULL, 
    email VARCHAR(50) NOT NULL, 
    course VARCHAR(50) NOT NULL, 
    mobile_number BIGINT NOT NULL
);

4. Applications Table :
   
This table tracks student applications for various job openings, including the status of their application.

sql :

CREATE TABLE application (
    application_id INT PRIMARY KEY AUTO_INCREMENT, 
    student_id VARCHAR(15) NOT NULL, 
    FOREIGN KEY(student_id) REFERENCES student(rollnumber), 
    coordinator_id INT NOT NULL, 
    FOREIGN KEY(coordinator_id) REFERENCES coordinator(coordinator_id), 
    job_id INT NOT NULL,  
    FOREIGN KEY(job_id) REFERENCES job_opening(job_id), 
    name VARCHAR(50) NOT NULL, 
    dob DATE NOT NULL, 
    branch VARCHAR(100) NOT NULL, 
    email VARCHAR(50) NOT NULL, 
    phone_number BIGINT NOT NULL, 
    cgpa DECIMAL(4, 2) NOT NULL, 
    status VARCHAR(255) DEFAULT 'pending'
);

5. Head of the Placement Cell :
   
This table stores details of the head of the Placement Cell.

sql :

CREATE TABLE head (
    firstname VARCHAR(28) NOT NULL, 
    lastname VARCHAR(28) NOT NULL, 
    email VARCHAR(28) PRIMARY KEY, 
    mobile_number BIGINT, 
    password VARCHAR(16) NOT NULL
);

6. Coordinator Table :
   
This table stores details about the coordinators who shortlist applicants.

sql :

CREATE TABLE coordinator (
    coordinator_id INT PRIMARY KEY, 
    firstname VARCHAR(28) NOT NULL, 
    lastname VARCHAR(28) NOT NULL, 
    email VARCHAR(28) NOT NULL, 
    mobile_number BIGINT, 
    password VARCHAR(16) NOT NULL
);

Running the Flask Application :

After setting up the database and inserting sample data, you can run the Flask application by executing the app.py file. This will launch the application, and you can begin using the platform for student registrations, job postings, and recruiter interactions.

