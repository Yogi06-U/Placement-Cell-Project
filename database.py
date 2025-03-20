import mysql.connector
import random
db_config = {
    'host': 'localhost',            # Your MySQL host
    'user': 'root',                 # Your MySQL username
    'password': 'Your Password',     # Your MySQL password
    'database': 'pcell'             # Your Database name
}

def create_tables():
    connection = get_db_connection()
    cursor = connection.cursor()
    #cursor.execute('create table company(company_name varchar(28) primary key, logo_url varchar(2048) not null, password varchar(16) not null, company_email varchar(56) not null, linkedin_url varchar(2048))')
    #cursor.execute('create table job_opening(job_id int primary key AUTO_INCREMENT, job_title varchar(30) not null, opening_status varchar(10) not null, job_type varchar(25) not null, salary int not null, Benefits varchar(200) not null, location varchar(40) not null, interview_date date not null, company_name varchar(28) not null,  foreign key(company_name) references company(company_name), cgpa DECIMAL(4, 2) not null)')
    #cursor.execute('create table student(rollnumber varchar(15) primary key, firstname varchar(28) not null, lastname varchar(28) not null, year_of_grad int not null, email varchar(50) not null, course varchar(50) not null, mobile_number bigint not null)')
    #cursor.execute('create table application(application_id int primary key auto_increment, student_id varchar(15) not null, foreign key(student_id) references student(rollnumber), coordinator_id int not null, foreign key(coordinator_id) references coordinator(coordinator_id), job_id int not null,  foreign key(job_id) references job_opening(job_id), name varchar(50) not null, dob date not null, branch varchar(100) not null, email varchar(50) not null, phone_number bigint not null, cgpa DECIMAL(4, 2) not null, status varchar(255) default "pending")')
    #cursor.execute('create table head(firstname varchar(28) not null, lastname varchar(28) not null, email varchar(28) primary key, mobile_number bigint, password varchar(16) not null)')
    #cursor.execute('create table coordinator(coordinator_id int primary key, firstname varchar(28) not null, lastname varchar(28) not null, email varchar(28) not null, mobile_number bigint, password varchar(16) not null)')
    
    cursor.close()
    connection.close()
    
def get_db_connection():
    connection = mysql.connector.connect(**db_config)
    return connection 

def get_recruiters():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT company_name, logo_url FROM company")
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    recruiters = []
    for row in data:
        company_name, logo_url = row
        recruiter = {
            'company_name': company_name,
            'logo_url': logo_url
        }
        recruiters.append(recruiter)
    return recruiters
      

def signup_student(rollnumber, email, password):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT password FROM student WHERE rollnumber = %s", (rollnumber,))
    result = cursor.fetchone()
    
    if result is None:
        cursor.close()
        connection.close()
        return "Roll number not found."
    existing_password = result[0]

    if existing_password is not None:
        cursor.close()
        connection.close()
        return "Student already signed up."

    cursor.execute("UPDATE student SET password = %s WHERE rollnumber = %s", (password, rollnumber))
    connection.commit()  
    cursor.close()
    connection.close()

    return "Signup successful."

def authenticate_student(email, password):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT rollnumber, firstname, lastname, year_of_grad, email, course, mobile_number, password FROM student WHERE email = %s", (email,))
    student_data = cursor.fetchone()
    
    cursor.close()
    connection.close()

    if student_data:
        rollnumber, firstname, lastname, year_of_grad, email, course, mobile_number, stored_password = student_data
        
        if stored_password == password:

            return {
                'rollnumber': rollnumber,
                'firstname': firstname,
                'lastname': lastname,
                'year_of_grad': year_of_grad,
                'email': email,
                'course': course,
                'mobile_number': mobile_number
            }
    
    return None

def authenticate_company(email, password):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT company_name, logo_url, password, linkedin_url FROM company WHERE company_email = %s", (email,))
    company_data = cursor.fetchone()
    
    cursor.close()
    connection.close()

    if company_data:
        company_name, logo_url, stored_password, linkedin_url = company_data
        
        if stored_password == password:
            return {
                'company_name': company_name,
                'logo_url': logo_url,
                'company_email': email,
                'linkedin_url': linkedin_url,
            }
    
    return None

def authenticate_coordinator(email, password):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT coordinator_id, firstname, lastname, email, mobile_number, password, year FROM coordinator WHERE email = %s", (email,))
    coordinator_data = cursor.fetchone()
    
    cursor.close()
    connection.close()

    if coordinator_data:
        coordinator_id, firstname, lastname, email, mobile_number, stored_password, year = coordinator_data
        
        if stored_password == password:
            return {
                'coordinator_id': coordinator_id,
                'firstname': firstname,
                'lastname': lastname,
                'email': email,
                'mobile_number': mobile_number,
                'year' : year
            }
    
    return None

def get_applications_with_coordinator(coordinator_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute("""
        SELECT application_id, student_id, coordinator_id, job_id, name, dob, branch, email, phone_number, cgpa, status 
        FROM application 
        WHERE coordinator_id = %s
    """, (coordinator_id,))
    
    applications = cursor.fetchall()
    cursor.close()
    connection.close()
    
    application_list = []
    for row in applications:
        application = {
            'application_id': row[0],
            'student_id': row[1],
            'coordinator_id': row[2],
            'job_id': row[3],
            'name': row[4],
            'dob': row[5],
            'branch': row[6],
            'email': row[7],
            'phone_number': row[8],
            'cgpa': row[9],
            'status': row[10]
        }
        application_list.append(application)
    
    return application_list

def get_applications_with_coordinator(coordinator_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute("""
        SELECT a.application_id, a.student_id, a.coordinator_id, a.job_id, a.name AS application_name, a.dob, a.branch, a.email, a.phone_number, a.cgpa, 
               s.firstname, s.lastname, j.company_name 
        FROM application a
        JOIN student s ON a.student_id = s.rollnumber
        JOIN job_opening j ON a.job_id = j.job_id
        WHERE a.coordinator_id = %s and a.status = 'pending'
    """, (coordinator_id,))
    
    applications = cursor.fetchall()
    cursor.close()
    connection.close()
    
    application_list = []
    for row in applications:
        application = {
            'application_id': row[0],
            'student_id': row[1],
            'coordinator_id': row[2],
            'job_id': row[3],
            'application_name': row[4],  # Name from the application table
            'dob': row[5],
            'branch': row[6],
            'email': row[7],
            'phone_number': row[8],
            'cgpa': row[9],
            'student_name': f"{row[10]} {row[11]}",  # Concatenate first and last name from the student table
            'company_name': row[12]  # Company name from the job_opening table
        }
        application_list.append(application)
    
    return application_list



def accept_application(application_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Update the status of the application to 'accepted'
    try:
        cursor.execute("""
            UPDATE application 
            SET status = 'accepted' 
            WHERE application_id = %s
        """, (application_id,))
        
        connection.commit()  # Commit the changes to the database
        
        if cursor.rowcount == 0:
            return "Application ID not found."
        
        return "Application accepted successfully."
    
    except mysql.connector.Error as err:
        return f"Error: {err}"
    
    finally:
        cursor.close()
        connection.close()

def reject_application(application_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("""
            UPDATE application 
            SET status = 'rejected' 
            WHERE application_id = %s
        """, (application_id,))
        
        connection.commit()  # Commit the changes to the database
        
        if cursor.rowcount == 0:
            return "Application ID not found."
        
        return "Application rejected successfully."
    
    except mysql.connector.Error as err:
        return f"Error: {err}"
    
    finally:
        cursor.close()
        connection.close()

def create_job_opening(company_name, job_details):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Extract details from the job_details dictionary
    job_title = job_details.get('job_title')
    opening_status = job_details.get('opening_status')
    job_type = job_details.get('job_type')
    salary = job_details.get('salary')
    benefits = job_details.get('Benefits')
    location = job_details.get('location')
    interview_date = job_details.get('interview_date')
    cgpa = job_details.get('cgpa')
    vacancies = job_details.get('vacancies')
    
    try:
        # Insert the new job opening into the job_opening table
        cursor.execute("""
    INSERT INTO job_opening (job_title, opening_status, job_type, salary, Benefits, location, company_name, cgpa, vacancies) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
""", (job_title, opening_status, job_type, salary, benefits, location, company_name, cgpa, vacancies))

        connection.commit()  # Commit the changes to the database
        
        return "Job opening created successfully."
    
    except mysql.connector.Error as err:
        return f"Error: {err}"
    
    finally:
        cursor.close()
        connection.close()        

def get_job_openings_with_company(company_name):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("""
            SELECT job_id, job_title, opening_status, job_type, salary, Benefits, location, company_name, cgpa, vacancies 
            FROM job_opening 
            WHERE company_name = %s and status = 'open';
        """, (company_name,))
        
        job_openings = cursor.fetchall()  # Fetch all job openings for the company
        job_list = []
        
        for row in job_openings:
            job = {
                'job_id': row[0],
                'job_title': row[1],
                'opening_status': row[2],
                'job_type': row[3],
                'salary': row[4],
                'Benefits': row[5],
                'location': row[6],
                'company_name': row[7],  # Added company_name to the dictionary
                'cgpa': row[8],
                'vacancies': row[9]  # Added vacancies to the dictionary
            }
            job_list.append(job)
        
        return job_list
    
    except mysql.connector.Error as err:
        return f"Error: {err}"
    
    finally:
        cursor.close()
        connection.close()       

def get_applications_with_company(company_name):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("""
            SELECT a.student_id, s.firstname, s.lastname, s.email, a.cgpa, j.job_title
            FROM application a
            JOIN student s ON a.student_id = s.rollnumber
            JOIN job_opening j ON a.job_id = j.job_id
            WHERE j.company_name = %s ;
        """, (company_name,))
        
        applications = cursor.fetchall()  # Fetch all applications for the specified company
        application_list = []
        
        for row in applications:
            application = {
                'student_id': row[0],
                'name': f"{row[1]} {row[2]}",  # Concatenate first and last name
                'email': row[3],
                'cgpa': row[4],
                'job_title' : row[5]
            }
            application_list.append(application)
        
        return application_list
    
    except mysql.connector.Error as err:
        return f"Error: {err}"
    
    finally:
        cursor.close()
        connection.close()

def close_job_opening(job_id):
    connection = get_db_connection()  # Ensure this function returns a valid connection
    cursor = connection.cursor()
    
    try:
        # Update the status of the job opening to 'closed'
        cursor.execute("UPDATE job_opening SET status = 'closed' WHERE job_id = %s", (job_id,))
        connection.commit()  # Commit the transaction
        
        if cursor.rowcount == 0:
            return "No records updated. Job ID may not exist."
        
        return "Job opening closed successfully."
    
    except Exception as e:
        connection.rollback()  # Rollback in case of error
        return f"An error occurred: {str(e)}"
    
    finally:
        cursor.close()
        connection.close()

def get_open_job_openings():
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                j.job_id,
                j.job_title,
                j.opening_status,
                j.job_type,
                j.salary,
                j.Benefits,
                j.location,
                j.cgpa,
                j.vacancies,
                j.status,
                c.company_name,
                c.logo_url
            FROM 
                job_opening j
            JOIN 
                company c ON j.company_name = c.company_name
            WHERE 
                j.status = 'open';  -- Filter for job openings with status 'open'
        """)
        
        job_openings = cursor.fetchall()  # Fetch all job openings that are open
        job_list = []
        
        for row in job_openings:
            job = {
                'job_id': row[0],
                'job_title': row[1],
                'opening_status': row[2],
                'job_type': row[3],
                'salary': row[4],
                'Benefits': row[5],
                'location': row[6],
                'cgpa': row[7],
                'vacancies': row[8],
                'status': row[9],
                'company_name': row[10],  # Company name from the company table
                'logo_url': row[11]  # Logo URL from the company table
            }
            job_list.append(job)
        
        return job_list
    
    except mysql.connector.Error as err:
        return f"Error: {err}"
    
    finally:
        cursor.close()
        connection.close()

def update_student_info(rollnumber, mobile_number, email, year_of_grad, course):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        # Update the student's information in the database
        cursor.execute("""
            UPDATE student 
            SET mobile_number = %s, email = %s, year_of_grad = %s, course = %s 
            WHERE rollnumber = %s
        """, (mobile_number, email, year_of_grad, course, rollnumber))
        
        connection.commit()  # Commit the changes to the database
        
        if cursor.rowcount == 0:
            return None  # No changes made or roll number not found.
        
        # Fetch the updated student information
        cursor.execute("SELECT firstname, lastname, year_of_grad, email, course, mobile_number, password FROM student WHERE rollnumber = %s", (rollnumber,))
        updated_student = cursor.fetchone()
        
        if updated_student:
            return {
                'rollnumber': rollnumber,
                'firstname': updated_student[0],
                'lastname': updated_student[1],
                'year_of_grad': updated_student[2],
                'email': updated_student[3],
                'course': updated_student[4],
                'mobile_number': updated_student[5],
                'password': updated_student[6]  # Be cautious about returning passwords
            }
        
        return None  # In case no student is found
    
    except mysql.connector.Error as err:
        return f"Error: {err}"
    
    finally:
        cursor.close()
        connection.close()

def get_application_with_student(rollnumber):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("""
            SELECT a.application_id, a.job_id, j.company_name, j.job_title, a.status
            FROM application a
            JOIN job_opening j ON a.job_id = j.job_id
            WHERE a.student_id = %s
        """, (rollnumber,))
        
        applications = cursor.fetchall()  # Fetch all applications for the specified rollnumber
        application_list = []
        
        for row in applications:
            application = {
                'application_id': row[0],
                'job_id': row[1],
                'company_name': row[2],
                'job_title': row[3],  # Added job_title to the dictionary
                'status': row[4]
            }
            application_list.append(application)
        
        return application_list
    
    except mysql.connector.Error as err:
        return f"Error: {err}"
    
    finally:
        cursor.close()
        connection.close()



def get_random_coordinator_id():
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("SELECT coordinator_id FROM coordinator")  # Assuming you have a coordinators table
        coordinators = cursor.fetchall()
        
        if coordinators:
            # Randomly select a coordinator ID
            coordinator_id = random.choice([c[0] for c in coordinators])  # Extract coordinator IDs from tuples
            return 1 #coordinator_id
        else:
            return None  # No coordinators available

    except Exception as e:
        return None  # Handle any exceptions and return None

    finally:
        cursor.close()
        connection.close()

def create_application(student_id, coordinator_id, job_id, name, branch, email, phone_number, cgpa, dob):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO application (student_id, coordinator_id, job_id, name, branch, email, phone_number, cgpa, dob, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'Pending')
        """, (student_id, coordinator_id, job_id, name, branch, email, phone_number, cgpa, dob))
        
        connection.commit()  # Commit the transaction
        return "Application submitted successfully."
    
    except Exception as e:
        connection.rollback()  # Rollback in case of error
        return f"Error submitting application: {e}"
    
    finally:
        cursor.close()
        connection.close()

def authenticate_head(email, password):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("SELECT firstname, lastname, email, mobile_number, password FROM head WHERE email = %s", (email,))
        head_data = cursor.fetchone()
        
        if head_data:
            firstname, lastname, stored_email, mobile_number, stored_password = head_data
            
            if stored_password == password:
                return {
                    'firstname': firstname,
                    'lastname': lastname,
                    'email': stored_email,
                    'mobile_number': mobile_number
                }
        
        return None  # Return None if authentication fails
    
    except mysql.connector.Error as err:
        return f"Error: {err}"
    
    finally:
        cursor.close()
        connection.close()

def get_students():
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("SELECT rollnumber, firstname, lastname, email, year_of_grad FROM student")
        rows = cursor.fetchall()
        
        # Convert each row into a dictionary
        students = []
        for row in rows:
            student = {
                'rollnumber': row[0],
                'firstname': row[1],
                'lastname': row[2],
                'email': row[3],
                'year_of_grad': row[4]
            }
            students.append(student)
        
        return students  # This will return a list of dictionaries
    
    except mysql.connector.Error as err:
        return f"Error: {err}"
    
    finally:
        cursor.close()
        connection.close()

def get_coordinators():
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute(""" 
            SELECT coordinator_id, firstname, lastname, email, mobile_number 
            FROM coordinator 
        """)
        
        coordinators = cursor.fetchall()  # Fetch all coordinators
        coordinator_list = []
        
        for row in coordinators:
            coordinator = {
                'coordinator_id': row[0],
                'firstname': row[1],
                'lastname': row[2],
                'email': row[3],
                'mobile_number': row[4]
            }
            coordinator_list.append(coordinator)
        
        return coordinator_list
    
    except mysql.connector.Error as err:
        return f"Error: {err}"
    
    finally:
        cursor.close()
        connection.close()

def get_companies():
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("SELECT company_name, company_email FROM company")
        rows = cursor.fetchall()
        
        # Convert each row into a dictionary
        companies = []
        for row in rows:
            company = {
                'company_name': row[0],
                'company_email': row[1]
            }
            companies.append(company)
        
        return companies  # This will return a list of dictionaries
    
    except mysql.connector.Error as err:
        return f"Error: {err}"
    
    finally:
        cursor.close()
        connection.close()