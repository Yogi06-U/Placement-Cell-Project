from flask import Flask, render_template, request, redirect,jsonify, url_for, flash, session
import database
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.config['SECRET_KEY'] = 'IIITK PLACEMENT CELL'

@app.route('/')
def p_cell():
    connection = database.get_db_connection()
    cursor = connection.cursor() 
    recruiters = database.get_recruiters()
    cursor.close()
    connection.close()
    return render_template('index.html', recruiters = recruiters)
    

@app.route('/student/signup', methods=['GET', 'POST'])
def student_signup():
    if request.method == 'POST':
        roll_number = request.form['rollnumber']
        email = request.form['email']
        password = request.form['password']
        
         # Fetch the OTP from the database
        connection = database.get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT otp FROM student where rollnumber = %s",(roll_number,))
        stored_otp = cursor.fetchone()
        stored_otp = stored_otp[0]
        cursor.close()
        connection.close()

        # If no OTP is found or if the user is not yet registered, handle accordingly
        if stored_otp is None:
            return jsonify({"error": "No OTP generated for this email."}), 400
        
        # Get the OTP provided by the user
        otpp = request.form['otp']
        print(otpp)
        print(stored_otp)
        print(stored_otp==otpp)
        # Compare the provided OTP with the stored OTP
        if str(otpp) != str(stored_otp):  # stored_otp[0] contains the OTP
            flash("Invalid OTP"),
        
        message = database.signup_student(roll_number, email, password)
        if message == "Signup successful.":
            flash(message)
            return redirect(url_for('student_login'))
        
    return render_template('student_signup.html')

@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        student = database.authenticate_student(email, password)

        if student is not None:
            # You can store the student data in the session if needed
            session['student'] = student
            flash("Login successful!")
            return redirect(url_for('student_dashboard'))  # Redirect to the student profile page
        else:
            flash("Invalid email or password. Please try again.")

    return render_template('student_login.html')

@app.route('/student/profile')
def student_profile():
    student = session.get('student')
    if student is None:
        flash("You need to log in first.")
        return redirect(url_for('student_login'))
    rollnumber = student['rollnumber']
    applications = database.get_application_with_student(rollnumber)
    return render_template('student_profile.html', student = student, applications = applications)

@app.route('/student/dashboard')
def student_dashboard():
    student = session.get('student')
    if student is None:
        flash("You need to log in first.")
        return redirect(url_for('student_login'))
    # Retrieve all job openings using the get_job_openings function
    job_openings = database.get_open_job_openings()  # Ensure this function is defined in the database module
    
    # Render the student dashboard template and pass the job openings data
    return render_template('student_dashboard.html', job_openings=job_openings)

@app.route('/student/update_info', methods=['POST'])
def update_info():
    student = session.get('student')
    if student is None:
        flash("You need to log in first.")
        return redirect(url_for('student_login'))

    rollnumber = student['rollnumber']  # Assuming 'rollnumber' is stored in the student session

    mobile_number = request.form['mobile_number']
    email = request.form['email']
    year_of_grad = request.form['year_of_grad']
    course = request.form['course']

    # Call the update_student_info function from the database module
    updated_student_info = database.update_student_info(rollnumber, mobile_number, email, year_of_grad, course)

    if updated_student_info:
        # Update session with new student info if needed
        session['student'] = updated_student_info
        flash("Student information updated successfully.")
    else:
        flash("No changes made or roll number not found.")

    # Redirect to the student profile page or return updated info as needed
    return redirect(url_for('student_profile'))

@app.route('/send_application', methods=['POST'])
def send_application():
    student = session.get('student')
    if student is None:
        flash("You need to log in first.")
        return redirect(url_for('student_login'))

    # Extract data from the form
    student_id = student['rollnumber']  # Assuming rollnumber is the student_id
    job_id = request.form['job_id']  # Get job_id from the form
    name = request.form['name']
    branch = request.form['course']
    email = request.form['email']
    phone_number = request.form['mobile_number']
    cgpa = request.form['cgpa']
    dob = request.form['dob']

    # Get a random coordinator ID from available coordinators
    coordinator_id = database.get_random_coordinator_id()
    # Create application with the collected data
    result = database.create_application(student_id, coordinator_id, job_id, name, branch, email, phone_number, cgpa, dob)

    flash(result)  # Flash the result message (success or error)
    return redirect(url_for('student_dashboard'))  # Redirect to the student dashboard or profile page

@app.route('/enroll', methods=['POST'])
def enroll():
    # Retrieve job_id from the form data
    job_id = request.form.get('job_id')
    # Retrieve student ID from the session
    student = session.get('student')
    if student is None:
        flash("You need to log in first.")
        return redirect(url_for('student_login'))

    student_id = student['rollnumber']  # Assuming rollnumber is the student ID

    # Render the enroll_form template, passing job_id and student_id
    return render_template('enroll_form.html', job_id=job_id, student_id=student_id)

@app.route('/coordinator/login', methods=['GET', 'POST'])
def coordinator_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Use the authenticate_coordinator function from the database module
        coordinator = database.authenticate_coordinator(email, password)

        if coordinator is not None:
            # Store the coordinator data in the session
            session['coordinator'] = coordinator  # This assumes 'coordinator' is a dictionary with coordinator data
            flash("Login successful!")
            return redirect(url_for('coordinator_dashboard'))  # Redirect to the coordinator dashboard
        else:
            flash("Invalid email or password. Please try again.")

    return render_template('coordinator_login.html')

@app.route('/coordinator/dashboard')
def coordinator_dashboard():
    coordinator = session.get('coordinator')  
    if coordinator is None:
        flash("You need to log in first.")
        return redirect(url_for('coordinator_login'))  
    applications = database.get_applications_with_coordinator(coordinator['coordinator_id'])
    return render_template('coordinator_dashboard.html', coordinator=coordinator, applications = applications)

@app.route('/accept_application', methods=['POST'])
def accept_application():
    application_id = request.form.get('application_id')
    result = database.accept_application(application_id)
    flash(result)
    return redirect(url_for('coordinator_dashboard'))  

@app.route('/reject_application', methods=['POST'])
def handle_reject_application():
    application_id = request.form.get('application_id')
    result = database.reject_application(application_id)
    flash(result)  
    return redirect(url_for('coordinator_dashboard'))

@app.route('/company/login', methods=['GET', 'POST'])
def company_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Assuming you have a similar authenticate_company function in your database module
        company = database.authenticate_company(email, password)

        if company is not None:
            # Store the company data in the session
            session['company'] = company  # This assumes 'company' is a dictionary with company data
            flash("Login successful!")
            return redirect(url_for('company_dashboard'))  # Redirect to the company profile page
        else:
            flash("Invalid email or password. Please try again.")

    return render_template('company_login.html')

@app.route('/company/dashboard')
def company_dashboard():
    company = session.get('company')  # Retrieve company data from the session
    if company is None:
        flash("You need to log in first.")
        return redirect(url_for('company_login'))  # Redirect to login if not logged in
    job_openings = database.get_job_openings_with_company(company['company_name'])
    candidates = database.get_applications_with_company(company['company_name'])
    return render_template('company_profile.html', company=company, job_openings = job_openings, candidates = candidates)

@app.route('/company/add_job_opening', methods=['GET', 'POST'])
def add_job_opening():
    if request.method == 'POST':
        # Get the company name from the session
        company = session.get('company')
        if company is None:
            flash("You need to log in first.")
            return redirect(url_for('company_login'))  # Redirect to login if not logged in

        company_name = company['company_name']  # Assuming the company name is stored in the session

        # Get job details from the form
        job_details = {
            'job_title': request.form['job_title'],
            'opening_status': 'open',
            'job_type': request.form['job_type'],
            'salary': request.form['salary'],
            'Benefits': request.form['Benefits'],
            'location': request.form['location'],
            'cgpa': request.form['cgpa'],
            'vacancies' : request.form['vacancies']
        }

        # Call the create_job_opening function from the database module
        result = database.create_job_opening(company_name, job_details)
        flash(result)  # Flash the result message to the user
        return redirect(url_for('company_dashboard'))  # Redirect to the company dashboard

    return render_template('add_job_opening.html')  # Render the form for adding a job opening

@app.route('/close_job_opening', methods=['POST'])
def close_job_opening():
    job_id = request.form.get('job_id')  # Get job_id from the form data
    print(job_id)
    if job_id:
        result = database.close_job_opening(job_id)
        flash(result)  # Flash the result message (success or error)
    
    return redirect(url_for('company_dashboard'))

@app.route('/head/login', methods=['GET', 'POST'])
def head_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print(email, password, sep='\n')
        # Use the authenticate_head function from the database module
        head = database.authenticate_head(email, password)

        if head is not None:
            # Store the head data in the session
            session['head'] = head  # This assumes 'head' is a dictionary with head data
            flash("Login successful!")
            return redirect(url_for('head_dashboard'))  # Redirect to the head dashboard
        else:
            flash("Invalid email or password. Please try again.")

    return render_template('head_login.html')

@app.route('/head/dashboard')
def head_dashboard():
    head = session.get('head')
    if head is None:
        flash("You need to login first!")
        return redirect(url_for('head_login'))
    # Retrieve accepted applications and coordinators using the database functions
    students = database.get_students()
    coordinators = database.get_coordinators()
    companies = database.get_companies()
    # Render the head.html template and pass the data
    return render_template('head_dashboard.html', students=students, coordinators=coordinators, companies = companies)
# Generate a random 6-digit OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# Send OTP via email
def send_otp_email(recipient_email, otp):
    sender_email = "iiitkplacementcell@gmail.com"
    sender_password = "rsbm hyfc huxi ajrl"  # Secure your credentials

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = "Your OTP Code"

    # Email body
    body = f"Your OTP code is {otp}. Please enter this code to verify your account."
    message.attach(MIMEText(body, 'plain'))

    try:
        # Setting up the SMTP server
        with smtplib.SMTP('smtp.gmail.com', 587) as server:  # Use your SMTP server and port
            server.starttls()  # Enable security
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
    

# Route to handle OTP request
@app.route('/send_otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    email = data.get('email')

    if email:
        otp = generate_otp()
        connection = database.get_db_connection()
        cursor = connection.cursor()
        cursor.execute("UPDATE student SET otp = %s", (otp,))
        connection.commit()
        cursor.close()
        connection.close()


        if send_otp_email(email, otp):
            return jsonify({"success": True, "message": "OTP sent successfully"})
        else:
            return jsonify({"success": False, "message": "Failed to send OTP"})
    return jsonify({"success": False, "message": "Invalid request"})

@app.route('/placementstats')
def placement_stats():
    return render_template('P_cell_stats.html')
@app.route('/coordinator')
def coordinator():
    return render_template("coordinator.html")
@app.route('/contact')
def contact():
    return render_template("contact.html")
@app.route('/stud_signup')
def signup():
    return render_template("student_signup.html")
@app.route('/coord')
def coord():
    return render_template("coordinator_dashboard.html")
@app.route('/good')
def good():
    coordinator = session.get('coordinator')
    print(coordinator['year'])
    return render_template("coordinator_profile.html", coordinator = coordinator)



if __name__ == '__main__':
    app.run(debug=True, port=8000)