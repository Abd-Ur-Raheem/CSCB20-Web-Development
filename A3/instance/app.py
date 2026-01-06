from flask import Flask, render_template, url_for, request, flash, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

app = Flask(__name__)

app.config['SECRET_KEY']='13d7ae8bcd15c286ba166b8678df9741cd12083f85458fdf307923aab6145d74'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///assignment3.db'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes = 10)
db = SQLAlchemy(app)

class Registered(db.Model):
    __tablename__='Registered'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    type = db.Column(db.String(100), nullable=False)
    Password = db.Column(db.String(100), nullable=False)
    feedbacks = db.relationship('Feedback', backref='Registered', lazy=True)
    marks = db.relationship('Marks', backref='student', lazy=True)

class Feedback(db.Model):
    __tablename__ = 'Feedback'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('Registered.id'), nullable=False)
    reviewed = db.Column(db.Boolean, default=False)

class Marks(db.Model):
    __tablename__ = 'Marks'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('Registered.id'), nullable=False)
    assignment_name = db.Column(db.String(50), nullable=False)
    grade = db.Column(db.Integer, nullable=True)
    due_date = db.Column(db.String(20), nullable=False)
    remark_request = db.Column(db.Text, nullable=True)
    remark_status = db.Column(db.String(20), default='No Requests Made')

@app.route('/')
@app.route('/index')
def index():
    pagename = 'Welcome'
    return render_template('index.html', pagename=pagename)

@app.route('/home')
def home():
    pagename = 'Home'
    return render_template('home.html', pagename=pagename)

@app.route('/anon', methods=['GET', 'POST'])
def anon():
    if not session.get('logged_in') or not session.get('user_id'):
        flash('Please login first to submit feedback.', 'error')
        return redirect(url_for('login'))
    
    user = Registered.query.get(session['user_id'])
    if user.type != 'student':
        flash('Only students can submit feedback.', 'error')
        return redirect(url_for('home'))
    
    pagename = 'Anonymous Feedback'
    instructors = Registered.query.filter_by(type='instructor').all()
    
    if request.method == 'POST':
        instructor_id = request.form['registered']
        feedback_content = (
            f"What I like about the instructor's teaching: {request.form['like_teaching']}\n"
            f"What I recommend to improve teaching: {request.form['improve_teaching']}\n"
            f"What I like about the labs: {request.form['like_labs']}\n"
            f"What I recommend to improve labs: {request.form['improve_labs']}"
        )
        
        feed = Feedback(content=feedback_content, instructor_id=instructor_id)
        db.session.add(feed)
        db.session.commit()
        
        flash('Your feedback has been submitted successfully!', 'success')
        return redirect(url_for('anon'))
    
    return render_template('anon.html', instructors=instructors, pagename=pagename)

@app.route('/view_feedback', methods=['GET', 'POST'])
def view_feedback():
    if not session.get('logged_in') or not session.get('user_id'):
        flash('Please login first.', 'error')
        return redirect(url_for('login'))
    
    user = Registered.query.get(session['user_id'])
    if user.type != 'instructor':
        flash('Access denied. Instructors only.', 'error')
        return redirect(url_for('home'))
    
    pagename = 'View Feedback'
    
    if request.method == 'POST':
        feedback_id = request.form.get('feedback_id')
        feedback = Feedback.query.get(feedback_id)
        if feedback and feedback.instructor_id == user.id:  
            feedback.reviewed = not feedback.reviewed  
            db.session.commit()
            flash('Feedback status updated successfully!', 'success')
        else:
            flash('Invalid feedback ID or unauthorized action.', 'error')
        return redirect(url_for('view_feedback'))
    
    feedbacks = Feedback.query.filter_by(instructor_id=user.id).all()
    
    return render_template('view_feedback.html', pagename=pagename, feedbacks=feedbacks)

@app.route('/assignments')
def assignments():
    pagename = 'Assignments'
    return render_template('assignments.html', pagename = pagename)
@app.route('/labs')
def labs():
    pagename = 'Labs'
    return render_template('labs.html', pagename = pagename)

@app.route('/lecture')
def lecture():
    pagename = 'Lecture Notes'
    return render_template('lecture.html', pagename = pagename)
@app.route('/syllabus')
def syllabus():
    pagename = 'Syllabus'
    return render_template('syllabus.html', pagename = pagename)
@app.route('/team')
def team():
    pagename = 'Course Team'
    return render_template('team.html', pagename = pagename)

@app.route('/instructor_marks')
def instructor_marks():
    if not session.get('logged_in') or not session.get('user_id'):
        flash('Please login first.', 'error')
        return redirect(url_for('login'))
    
    user = Registered.query.get(session['user_id'])
    if user.type != 'instructor':
        flash('Access denied. Instructors only.', 'error')
        return redirect(url_for('home'))
    
    pagename = 'Instructor Marks'
    students = Registered.query.filter_by(type='student').all()
    all_marks = Marks.query.all()
    
    return render_template('instructor_marks.html', pagename=pagename, instructor_name=user.name, students=students, marks=all_marks)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('home'))
    pagename = 'Login'
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = Registered.query.filter_by(name=username).first()
        if user and user.Password == password:  
            session['logged_in'] = True
            session['user_id'] = user.id
            session.permanent = True 
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.', 'error')
    return render_template('login.html', pagename=pagename)

@app.route('/logout')
def logout():
    session.pop('logged_in', default=None)
    session.pop('user_id', default=None)
    flash('You have been logged out.', 'success')
    pagename = 'Logout'
    return render_template('logout.html', pagename=pagename)

@app.context_processor
def inject_user():
    if session.get('logged_in') and session.get('user_id'):
        user = Registered.query.get(session.get('user_id'))
        return {'current_user': user}
    return {'current_user': None}

@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('logged_in'):
        return redirect(url_for('home'))
    pagename = 'Register'
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_type = request.form.get('type')  

        
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return redirect(url_for('register'))

    
        existing_user = Registered.query.filter_by(name=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'error')
            return redirect(url_for('register'))

        new_user = Registered(name=username, type=user_type, Password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', pagename=pagename)

@app.route('/s_marks')
def s_marks():
    if not session.get('logged_in') or not session.get('user_id'):
        flash('Please login first.', 'error')
        return redirect(url_for('login'))
    
    user = Registered.query.get(session['user_id'])
    if user.type != 'student':
        flash('Access denied. Students only.', 'error')
        return redirect(url_for('home'))
    
    pagename = 'Student Marks'
    student_marks = Marks.query.filter_by(student_id=user.id).all()
    
    return render_template('s_marks.html', pagename=pagename, student_name=user.name, marks=student_marks)

@app.route('/view_remarks', methods=['GET', 'POST'])
def view_remarks():
    if not session.get('logged_in') or not session.get('user_id'):
        flash('Please login first.', 'error')
        return redirect(url_for('login'))
    
    user = Registered.query.get(session['user_id'])
    if user.type != 'instructor':
        flash('Access denied. Instructors only.', 'error')
        return redirect(url_for('home'))
    
    pagename = 'View Remark Requests'
    
    if request.method == 'POST':
        mark_id = request.form.get('mark_id')
        action = request.form.get('action')
        mark = Marks.query.get(mark_id)
        
        if mark and mark.remark_request:
            if action == 'approve':
                mark.remark_status = 'Approved'
                flash('Remark request approved successfully!', 'success')
            elif action == 'reject':
                mark.remark_status = 'Rejected'
                flash('Remark request rejected successfully!', 'success')
            db.session.commit()
        else:
            flash('Invalid remark request.', 'error')
        return redirect(url_for('view_remarks'))
    
    remark_requests = Marks.query.filter(Marks.remark_request.isnot(None)).all()
    
    return render_template('view_remarks.html', pagename=pagename, remark_requests=remark_requests)

@app.route('/submit_remark', methods=['POST'])
def submit_remark():
    if not session.get('logged_in') or not session.get('user_id'):
        flash('Please login first.', 'error')
        return redirect(url_for('login'))
    
    user = Registered.query.get(session['user_id'])
    if user.type != 'student':
        flash('Access denied. Students only.', 'error')
        return redirect(url_for('home'))
    
    mark_id = request.form.get('mark_id')
    remark_text = request.form.get('remark_text')
    
    if not mark_id or not remark_text:
        flash('Missing data. Please provide a reason for the remark request.', 'error')
        return redirect(url_for('s_marks'))
    
    mark = Marks.query.get(mark_id)
    if not mark or mark.student_id != user.id:
        flash('Invalid mark.', 'error')
        return redirect(url_for('s_marks'))
    
    mark.remark_request = remark_text
    mark.remark_status = 'Pending'
    db.session.commit()
    
    flash('Remark request submitted successfully!', 'success')
    return redirect(url_for('s_marks'))

@app.route('/enter_mark', methods=['POST'])
def enter_mark():
    if not session.get('logged_in') or not session.get('user_id'):
        flash('Please login first.', 'error')
        return redirect(url_for('login'))
    
    user = Registered.query.get(session['user_id'])
    if user.type != 'instructor':
        flash('Access denied. Instructors only.', 'error')
        return redirect(url_for('home'))
    
    student_id = request.form.get('student_id')
    assignment_name = request.form.get('assignment_name')
    grade = request.form.get('grade')
    
    if not student_id or not assignment_name or not grade:
        flash('Missing data. Please fill in all fields.', 'error')
        return redirect(url_for('instructor_marks'))
    
    mark = Marks.query.filter_by(student_id=student_id, assignment_name=assignment_name).first()
    
    if mark:
        mark.grade = grade
    else:
        mark = Marks(
            student_id=student_id,
            assignment_name=assignment_name,
            due_date="N/A", 
            grade=grade,
            remark_status="No Requests Made"
        )
        db.session.add(mark)
    
    db.session.commit()
    
    flash('Marks updated successfully!', 'success')
    return redirect(url_for('instructor_marks'))

if __name__=='__main__':
    app.run(debug=True)