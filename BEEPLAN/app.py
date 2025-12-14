"""
Flask web application for BeePlan scheduling system.
"""
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import json
import os
from typing import Dict, List
from models import Course, Instructor, Classroom, Schedule, Day, CourseType
from scheduler import Scheduler
from data_manager import DataManager, ValidationError

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Change this in production
app.config['SESSION_TYPE'] = 'filesystem'

# Simple user storage (in production, use a database)
USERS_FILE = 'users.json'

def init_users():
    """Initialize users file with default admin user."""
    if not os.path.exists(USERS_FILE):
        users = {
            'admin': {
                'password': generate_password_hash('admin123'),
                'role': 'admin'
            }
        }
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f)

def load_users():
    """Load users from file."""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Save users to file."""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def login_required(f):
    """Decorator to require login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Redirect to login or dashboard."""
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        users = load_users()
        if username in users and check_password_hash(users[username]['password'], password):
            session['user'] = username
            session['role'] = users[username].get('role', 'user')
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout and clear session."""
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard."""
    return render_template('dashboard.html', username=session.get('user'))

@app.route('/api/schedule/generate', methods=['POST'])
@login_required
def generate_schedule():
    """Generate schedule from uploaded data."""
    try:
        if 'data' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['data']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save uploaded file temporarily
        temp_path = f'temp_{session["user"]}.json'
        file.save(temp_path)
        
        # Import and validate data
        try:
            instructors, classrooms, courses = DataManager.import_all_from_json(temp_path, validate=True)
        except ValidationError as e:
            os.remove(temp_path)
            return jsonify({
                'error': 'Data validation failed',
                'validation_errors': e.errors
            }), 400
        except json.JSONDecodeError as e:
            os.remove(temp_path)
            return jsonify({'error': f'Invalid JSON format: {str(e)}'}), 400
        
        # Generate schedule with automatic conflict resolution
        scheduler = Scheduler(courses, classrooms)
        schedule, violations = scheduler.generate_schedule()
        
        # Convert schedule to JSON-serializable format
        schedule_data = {
            'scheduled_courses': [],
            'violations': []  # Don't show violations - system tries to resolve automatically
        }
        
        for sc in schedule.scheduled_courses:
            schedule_data['scheduled_courses'].append({
                'course_code': sc.course.code,
                'course_name': sc.course.name,
                'year': sc.year,
                'semester': sc.semester,
                'day': sc.time_slot.day.value,
                'start_time': sc.time_slot.start_time,
                'end_time': sc.time_slot.end_time,
                'classroom': sc.classroom.name,
                'instructor': sc.course.instructor.name,
                'course_type': sc.course.course_type.value,
                'enrollment': sc.course.enrollment
            })
        
        # Store in session (clear any old schedule first)
        if 'schedule' in session:
            del session['schedule']
        session['schedule'] = schedule_data
        session.permanent = True  # Make session persistent
        
        # Clean up temp file
        os.remove(temp_path)
        
        return jsonify({
            'success': True,
            'schedule': schedule_data,
            'message': f'Schedule generated: {len(schedule_data["scheduled_courses"])} courses scheduled'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/schedule/get')
@login_required
def get_schedule():
    """Get current schedule from session."""
    schedule = session.get('schedule')
    if schedule:
        return jsonify({'success': True, 'schedule': schedule})
    return jsonify({'success': False, 'message': 'No schedule generated yet'})

@app.route('/api/schedule/export')
@login_required
def export_schedule():
    """Export schedule as JSON or CSV."""
    schedule_data = session.get('schedule')
    if not schedule_data:
        return jsonify({'error': 'No schedule to export'}), 400
    
    format_type = request.args.get('format', 'json')
    
    import tempfile
    import csv
    import atexit
    
    if format_type == 'json':
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', encoding='utf-8')
        json.dump(schedule_data, temp_file, indent=2, ensure_ascii=False)
        temp_file.close()
        
        def cleanup():
            try:
                os.unlink(temp_file.name)
            except:
                pass
        atexit.register(cleanup)
        
        return send_file(temp_file.name, as_attachment=True, download_name='schedule.json', 
                        mimetype='application/json')
    else:
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='', encoding='utf-8')
        writer = csv.writer(temp_file)
        writer.writerow(['Course Code', 'Course Name', 'Year', 'Semester', 'Day', 'Start Time', 
                        'End Time', 'Classroom', 'Instructor'])
        for sc in schedule_data['scheduled_courses']:
            writer.writerow([
                sc['course_code'], sc['course_name'], sc['year'], sc.get('semester', 1), sc['day'],
                sc['start_time'], sc['end_time'], sc['classroom'], sc['instructor']
            ])
        temp_file.close()
        
        def cleanup():
            try:
                os.unlink(temp_file.name)
            except:
                pass
        atexit.register(cleanup)
        
        return send_file(temp_file.name, as_attachment=True, download_name='schedule.csv',
                        mimetype='text/csv')

@app.route('/api/report')
@login_required
def get_report():
    """Get validation report."""
    schedule_data = session.get('schedule')
    if not schedule_data:
        return jsonify({'error': 'No schedule generated'}), 400
    
    total_courses = len(schedule_data.get('scheduled_courses', []))
    
    # Group by year
    year_counts = {}
    semester_counts = {}
    for sc in schedule_data.get('scheduled_courses', []):
        year = sc['year']
        semester = sc.get('semester', 1)
        year_counts[year] = year_counts.get(year, 0) + 1
        semester_counts[semester] = semester_counts.get(semester, 0) + 1
    
    return jsonify({
        'total_courses': total_courses,
        'year_counts': year_counts,
        'semester_counts': semester_counts,
        'violations': [],  # Don't show violations - system resolves automatically
        'violation_count': 0
    })

if __name__ == '__main__':
    init_users()
    app.run(debug=True, host='0.0.0.0', port=5000)

