# BeePlan - Course Schedule Generator

A Python-based web application that generates conflict-free course schedules for your department. The system manages constraints such as instructor availability, lab hours, and exam blocks.

## Features

- **Web-Based Interface**: Modern, responsive web application with login system
- **Conflict-Free Scheduling**: Automatically generates schedules that avoid conflicts
- **Visual Timetable**: Weekly timetable view with color-coded courses
- **Constraint Management**: Handles instructor availability, lab hours, exam blocks, and more
- **Import/Export**: Supports JSON and CSV file formats
- **Validation Reports**: Detailed reports of violations and conflicts
- **Multi-Year Support**: Generates schedules for 1st-4th year students

## Requirements

- Python 3.7+
- Flask 3.0.0+
- pandas

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Web Application (Recommended)

1. Start the web server:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. **Login**: Use default credentials:
   - Username: `admin`
   - Password: `admin123`

4. **Import Data**: Upload your JSON data file containing:
   - Instructors (with availability)
   - Classrooms/Labs (with capacity)
   - Courses (with enrollment, type, year)

5. **Generate Schedule**: Click "Generate Schedule" to create a conflict-free schedule

6. **View Timetable**: Switch between years (1-4) to view schedules

7. **View Report**: Click "View Report" to see validation results

8. **Export Schedule**: Download the schedule as JSON or CSV

### Desktop Application (Legacy)

1. Run the desktop application:
```bash
python main.py
```

2. Follow the same workflow as the web application

## Data Format

### Instructors JSON
```json
{
  "instructors": [
    {
      "name": "Dr. Smith",
      "availability": {
        "MONDAY": ["08:00-12:00", "15:00-17:00"],
        "TUESDAY": ["08:00-17:00"],
        "FRIDAY": ["08:00-13:00", "15:10-17:00"]
      },
      "max_hours_per_day": 4
    }
  ]
}
```

### Classrooms JSON
```json
{
  "classrooms": [
    {"name": "A101", "capacity": 50, "is_lab": false, "type": "classroom"},
    {"name": "B201", "capacity": 40, "is_lab": true, "type": "lab"}
  ]
}
```

### Courses JSON
```json
{
  "courses": [
    {
      "code": "CENG101",
      "name": "Introduction to Programming",
      "year": 1,
      "instructor": "Dr. Smith",
      "type": "theory",
      "hours_per_week": 3,
      "enrollment": 45,
      "department": "CENG",
      "is_elective": false,
      "requires_lab": true
    },
    {
      "code": "CENG101L",
      "name": "Introduction to Programming Lab",
      "year": 1,
      "instructor": "Dr. Smith",
      "type": "lab",
      "hours_per_week": 2,
      "enrollment": 30,
      "department": "CENG",
      "is_elective": false,
      "theory_course_code": "CENG101"
    }
  ]
}
```

## Scheduling Rules

The system enforces the following rules:

1. **Friday Exam Block**: No courses between 13:20-15:10 on Fridays
2. **Instructor Limits**: Maximum 4 hours of theory per day per lecturer
3. **Lab After Theory**: Lab sessions must be scheduled after their theory courses
4. **Year Conflicts**: Students cannot have overlapping courses in the same year
5. **3rd Year vs Electives**: 3rd-year courses should not overlap with electives
6. **CENG vs SENG Electives**: CENG and SENG electives must not overlap
7. **Lab Capacity**: Lab capacity must be ≤ 40 students
8. **Instructor Availability**: Courses can only be scheduled during instructor available hours
9. **Classroom Conflicts**: No two courses can use the same classroom at the same time

## Visual Indicators

- **Green**: Theory courses
- **Blue**: Lab courses
- **Red**: Conflicts detected
- **Yellow**: Friday exam block period

## Project Structure

```
BeePlan/
├── app.py               # Flask web application (main entry point)
├── main.py              # Desktop application entry point (legacy)
├── gui.py               # PyQt5 GUI implementation (legacy)
├── models.py            # Data models (Course, Instructor, etc.)
├── scheduler.py         # Scheduling algorithm
├── data_manager.py      # Import/export functionality
├── templates/           # HTML templates
│   ├── base.html        # Base template
│   ├── login.html       # Login page
│   └── dashboard.html   # Main dashboard
├── static/              # Static files
│   ├── css/             # Stylesheets
│   └── js/              # JavaScript files
├── requirements.txt     # Python dependencies
├── sample_data.json     # Sample data for testing
└── README.md           # This file
```

## Algorithm

The scheduler uses a constraint-based backtracking approach:

1. Sorts courses by priority (year, then enrollment)
2. Schedules theory courses first
3. Schedules lab courses after their theory courses
4. Validates each placement against all constraints
5. Reports violations and conflicts

## License

This project is provided as-is for educational and departmental use.

