"""
Data import/export functionality for BeePlan.
"""
import json
import csv
import re
from typing import List, Dict, Tuple
from models import (
    Course, Instructor, Classroom, Schedule, ScheduledCourse,
    TimeSlot, Day, CourseType
)


class ValidationError(Exception):
    """Custom exception for validation errors."""
    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__('\n'.join(errors))


class DataValidator:
    """Validates imported data against business rules."""
    
    @staticmethod
    def validate_instructors(data: dict) -> List[str]:
        """Validate instructors data."""
        errors = []
        instructors = data.get("instructors", [])
        
        if not instructors:
            errors.append("No instructors found in data")
            return errors
        
        instructor_names = set()
        for idx, instructor in enumerate(instructors):
            name = instructor.get("name", "").strip()
            if not name:
                errors.append(f"Instructor #{idx + 1}: Missing name")
                continue
            
            if name in instructor_names:
                errors.append(f"Instructor '{name}': Duplicate name")
            instructor_names.add(name)
            
            # Validate availability
            availability = instructor.get("availability", {})
            if not availability:
                errors.append(f"Instructor '{name}': No availability specified")
            
            for day_str, slots in availability.items():
                # Validate day name
                day_upper = day_str.upper()
                valid_days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
                if day_upper not in valid_days:
                    errors.append(f"Instructor '{name}': Invalid day '{day_str}'. Use: {', '.join(valid_days)}")
                
                # Validate Friday exam block
                if day_upper == "FRIDAY":
                    for slot in slots:
                        if DataValidator._time_overlaps_exam_block(slot):
                            errors.append(
                                f"Instructor '{name}': Friday availability '{slot}' overlaps with exam block (13:20-15:10)"
                            )
                
                # Validate time format
                if not isinstance(slots, list):
                    errors.append(f"Instructor '{name}': Availability for {day_str} must be a list")
                    continue
                
                for slot in slots:
                    if not DataValidator._validate_time_slot_format(slot):
                        errors.append(
                            f"Instructor '{name}': Invalid time format '{slot}' for {day_str}. Use format 'HH:MM-HH:MM' (24-hour)"
                        )
        
        return errors
    
    @staticmethod
    def validate_classrooms(data: dict) -> List[str]:
        """Validate classrooms data."""
        errors = []
        classrooms = data.get("classrooms", [])
        
        if not classrooms:
            errors.append("No classrooms found in data")
            return errors
        
        classroom_names = set()
        for idx, classroom in enumerate(classrooms):
            name = classroom.get("name", "").strip()
            if not name:
                errors.append(f"Classroom #{idx + 1}: Missing name")
                continue
            
            if name in classroom_names:
                errors.append(f"Classroom '{name}': Duplicate name")
            classroom_names.add(name)
            
            # Validate capacity
            capacity = classroom.get("capacity")
            if capacity is None:
                errors.append(f"Classroom '{name}': Missing capacity")
            elif not isinstance(capacity, int) or capacity <= 0:
                errors.append(f"Classroom '{name}': Invalid capacity (must be positive integer)")
            
            # Validate lab capacity
            is_lab = classroom.get("is_lab", False)
            if is_lab and capacity and capacity > 40:
                errors.append(
                    f"Lab '{name}': Capacity {capacity} exceeds maximum of 40 students"
                )
        
        return errors
    
    @staticmethod
    def validate_courses(data: dict, instructor_names: set, course_codes: set = None) -> List[str]:
        """Validate courses data."""
        errors = []
        courses = data.get("courses", [])
        
        if course_codes is None:
            course_codes = set()
        
        if not courses:
            errors.append("No courses found in data")
            return errors
        
        theory_courses = {}
        
        for idx, course in enumerate(courses):
            code = course.get("code", "").strip()
            if not code:
                errors.append(f"Course #{idx + 1}: Missing code")
                continue
            
            if code in course_codes:
                errors.append(f"Course '{code}': Duplicate code")
            course_codes.add(code)
            
            # Validate instructor name matches
            instructor_name = course.get("instructor", "").strip()
            if not instructor_name:
                errors.append(f"Course '{code}': Missing instructor")
            elif instructor_name not in instructor_names:
                errors.append(
                    f"Course '{code}': Instructor '{instructor_name}' not found in instructors list. "
                    f"Available instructors: {', '.join(sorted(instructor_names))}"
                )
            
            # Validate course type
            course_type = course.get("type", "").lower()
            if course_type not in ["theory", "lab"]:
                errors.append(f"Course '{code}': Invalid type '{course_type}'. Must be 'theory' or 'lab'")
            
            # Validate enrollment
            enrollment = course.get("enrollment")
            if enrollment is None:
                errors.append(f"Course '{code}': Missing enrollment")
            elif not isinstance(enrollment, int) or enrollment <= 0:
                errors.append(f"Course '{code}': Invalid enrollment (must be positive integer)")
            
            # Validate semester (allow 1-8 for cumulative semesters across 4 years)
            semester = course.get("semester")
            if semester is not None:
                if not isinstance(semester, int) or semester < 1 or semester > 8:
                    errors.append(f"Course '{code}': Invalid semester (must be between 1 and 8)")
            
            # Validate lab courses have theory_course_code
            if course_type == "lab":
                theory_code = course.get("theory_course_code")
                if not theory_code:
                    errors.append(
                        f"Lab course '{code}': Missing 'theory_course_code'. Lab courses must reference their theory course."
                    )
                elif theory_code == code:
                    errors.append(
                        f"Lab course '{code}': 'theory_course_code' cannot reference itself. "
                        f"It must reference a different theory course."
                    )
                else:
                    # Store for later validation
                    if theory_code not in theory_courses:
                        theory_courses[theory_code] = []
                    theory_courses[theory_code].append(code)
            
            # Store theory courses for lab validation
            if course_type == "theory":
                theory_courses[code] = []
        
        # Validate that lab courses reference existing theory courses
        for theory_code, lab_courses in theory_courses.items():
            if theory_code not in course_codes:
                for lab_code in lab_courses:
                    errors.append(
                        f"Lab course '{lab_code}': Theory course '{theory_code}' not found in courses list"
                    )
        
        return errors
    
    @staticmethod
    def validate_enrollment_vs_capacity(courses: List[dict], classrooms: List[dict]) -> List[str]:
        """Validate that course enrollment doesn't exceed available classroom capacity."""
        errors = []
        
        for course in courses:
            course_type = course.get("type", "").lower()
            enrollment = course.get("enrollment", 0)
            
            if not isinstance(enrollment, int) or enrollment <= 0:
                continue
            
            # Find suitable classrooms
            suitable_classrooms = [
                c for c in classrooms
                if (course_type == "lab" and c.get("is_lab", False)) or
                   (course_type == "theory" and not c.get("is_lab", False))
            ]
            
            if not suitable_classrooms:
                errors.append(
                    f"Course '{course.get('code')}': No suitable {'lab' if course_type == 'lab' else 'classroom'} available"
                )
                continue
            
            # Check if any classroom can accommodate
            max_capacity = max(c.get("capacity", 0) for c in suitable_classrooms)
            if enrollment > max_capacity:
                errors.append(
                    f"Course '{course.get('code')}': Enrollment {enrollment} exceeds maximum "
                    f"{'lab' if course_type == 'lab' else 'classroom'} capacity of {max_capacity}"
                )
        
        return errors
    
    @staticmethod
    def _validate_time_slot_format(time_slot: str) -> bool:
        """Validate time slot format: HH:MM-HH:MM"""
        if not isinstance(time_slot, str):
            return False
        pattern = r'^\d{2}:\d{2}-\d{2}:\d{2}$'
        if not re.match(pattern, time_slot):
            return False
        try:
            start, end = time_slot.split('-')
            start_h, start_m = map(int, start.split(':'))
            end_h, end_m = map(int, end.split(':'))
            if not (0 <= start_h < 24 and 0 <= start_m < 60 and
                    0 <= end_h < 24 and 0 <= end_m < 60):
                return False
            if start_h * 60 + start_m >= end_h * 60 + end_m:
                return False
            return True
        except:
            return False
    
    @staticmethod
    def _time_to_minutes(time_str: str) -> int:
        """Convert time string to minutes."""
        h, m = map(int, time_str.split(':'))
        return h * 60 + m
    
    @staticmethod
    def _time_overlaps_exam_block(time_slot: str) -> bool:
        """Check if time slot overlaps with Friday exam block (13:20-15:10)."""
        try:
            start, end = time_slot.split('-')
            start_min = DataValidator._time_to_minutes(start)
            end_min = DataValidator._time_to_minutes(end)
            exam_start = DataValidator._time_to_minutes("13:20")
            exam_end = DataValidator._time_to_minutes("15:10")
            return not (end_min <= exam_start or start_min >= exam_end)
        except:
            return False
    
    @staticmethod
    def validate_all(data: dict) -> Tuple[bool, List[str]]:
        """Validate all data and return (is_valid, errors)."""
        all_errors = []
        
        # Validate instructors
        instructor_errors = DataValidator.validate_instructors(data)
        all_errors.extend(instructor_errors)
        
        # Get instructor names for course validation
        instructor_names = {inst.get("name", "").strip() for inst in data.get("instructors", [])}
        instructor_names = {name for name in instructor_names if name}
        
        # Validate classrooms
        classroom_errors = DataValidator.validate_classrooms(data)
        all_errors.extend(classroom_errors)
        
        # Validate courses
        course_errors = DataValidator.validate_courses(data, instructor_names)
        all_errors.extend(course_errors)
        
        # Validate enrollment vs capacity
        enrollment_errors = DataValidator.validate_enrollment_vs_capacity(
            data.get("courses", []),
            data.get("classrooms", [])
        )
        all_errors.extend(enrollment_errors)
        
        return len(all_errors) == 0, all_errors


class DataManager:
    """Handles import/export of scheduling data."""
    
    @staticmethod
    def export_schedule_to_json(schedule: Schedule, filename: str):
        """Export schedule to JSON file."""
        data = {
            "scheduled_courses": [],
            "violations": schedule.violations
        }
        
        for sc in schedule.scheduled_courses:
            data["scheduled_courses"].append({
                "course_code": sc.course.code,
                "course_name": sc.course.name,
                "year": sc.year,
                "day": sc.time_slot.day.value,
                "start_time": sc.time_slot.start_time,
                "end_time": sc.time_slot.end_time,
                "classroom": sc.classroom.name,
                "instructor": sc.course.instructor.name
            })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def export_schedule_to_csv(schedule: Schedule, filename: str):
        """Export schedule to CSV file."""
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Course Code", "Course Name", "Year", "Semester", "Day", "Start Time",
                "End Time", "Classroom", "Instructor"
            ])
            
            for sc in schedule.scheduled_courses:
                writer.writerow([
                    sc.course.code,
                    sc.course.name,
                    sc.year,
                    sc.semester,
                    sc.time_slot.day.value,
                    sc.time_slot.start_time,
                    sc.time_slot.end_time,
                    sc.classroom.name,
                    sc.course.instructor.name
                ])
    
    @staticmethod
    def import_courses_from_json(filename: str, instructors: Dict[str, Instructor]) -> List[Course]:
        """Import courses from JSON file."""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        courses = []
        for item in data.get("courses", []):
            instructor = instructors.get(item["instructor"])
            if not instructor:
                instructor = Instructor(name=item["instructor"])
                instructors[item["instructor"]] = instructor
            
            course = Course(
                code=item["code"],
                name=item["name"],
                year=item["year"],
                semester=item.get("semester", 1),  # Default to semester 1 if not specified
                instructor=instructor,
                course_type=CourseType.THEORY if item.get("type") == "theory" else CourseType.LAB,
                hours_per_week=item.get("hours_per_week", 3),
                enrollment=item.get("enrollment", 30),
                department=item.get("department", ""),
                is_elective=item.get("is_elective", False),
                requires_lab=item.get("requires_lab", False),
                theory_course_code=item.get("theory_course_code")
            )
            courses.append(course)
        
        return courses
    
    @staticmethod
    def import_classrooms_from_json(filename: str) -> List[Classroom]:
        """Import classrooms from JSON file."""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        classrooms = []
        for item in data.get("classrooms", []):
            classroom = Classroom(
                name=item["name"],
                capacity=item["capacity"],
                is_lab=item.get("is_lab", False),
                type=item.get("type", "classroom")
            )
            classrooms.append(classroom)
        
        return classrooms
    
    @staticmethod
    def import_instructors_from_json(filename: str) -> Dict[str, Instructor]:
        """Import instructors from JSON file."""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        instructors = {}
        for item in data.get("instructors", []):
            availability = {}
            for day_str, slots in item.get("availability", {}).items():
                try:
                    day = Day[day_str.upper()]
                    availability[day] = slots
                except KeyError:
                    # Try to match by value
                    for d in Day:
                        if d.value.upper() == day_str.upper():
                            availability[d] = slots
                            break
            
            instructor = Instructor(
                name=item["name"],
                availability=availability,
                max_hours_per_day=item.get("max_hours_per_day", 4)
            )
            instructors[instructor.name] = instructor
        
        return instructors
    
    @staticmethod
    def import_all_from_json(filename: str, validate: bool = True) -> tuple:
        """Import all data (instructors, classrooms, courses) from a single JSON file.
        
        Args:
            filename: Path to JSON file
            validate: If True, validate data before importing
            
        Returns:
            Tuple of (instructors, classrooms, courses)
            
        Raises:
            ValidationError: If validation fails and validate=True
        """
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate data if requested
        if validate:
            is_valid, errors = DataValidator.validate_all(data)
            if not is_valid:
                raise ValidationError(errors)
        
        # Import instructors first
        instructors = {}
        for item in data.get("instructors", []):
            availability = {}
            for day_str, slots in item.get("availability", {}).items():
                try:
                    day = Day[day_str.upper()]
                    availability[day] = slots
                except KeyError:
                    # Try to match by value
                    for d in Day:
                        if d.value.upper() == day_str.upper():
                            availability[d] = slots
                            break
            
            instructor = Instructor(
                name=item["name"],
                availability=availability,
                max_hours_per_day=item.get("max_hours_per_day", 4)
            )
            instructors[instructor.name] = instructor
        
        # Import classrooms
        classrooms = []
        for item in data.get("classrooms", []):
            classroom = Classroom(
                name=item["name"],
                capacity=item["capacity"],
                is_lab=item.get("is_lab", False),
                type=item.get("type", "classroom")
            )
            classrooms.append(classroom)
        
        # Import courses
        courses = []
        for item in data.get("courses", []):
            instructor = instructors.get(item["instructor"])
            if not instructor:
                instructor = Instructor(name=item["instructor"])
                instructors[item["instructor"]] = instructor
            
            course = Course(
                code=item["code"],
                name=item["name"],
                year=item["year"],
                semester=item.get("semester", 1),  # Default to semester 1 if not specified
                instructor=instructor,
                course_type=CourseType.THEORY if item.get("type") == "theory" else CourseType.LAB,
                hours_per_week=item.get("hours_per_week", 3),
                enrollment=item.get("enrollment", 30),
                department=item.get("department", ""),
                is_elective=item.get("is_elective", False),
                requires_lab=item.get("requires_lab", False),
                theory_course_code=item.get("theory_course_code")
            )
            courses.append(course)
        
        return instructors, classrooms, courses
    
    @staticmethod
    def create_sample_data():
        """Create sample data files for testing."""
        # Sample instructors
        instructors_data = {
            "instructors": [
                {
                    "name": "Dr. Smith",
                    "availability": {
                        "MONDAY": ["08:00-12:00", "15:00-17:00"],
                        "TUESDAY": ["08:00-17:00"],
                        "WEDNESDAY": ["08:00-12:00"],
                        "THURSDAY": ["08:00-17:00"],
                        "FRIDAY": ["08:00-13:00", "15:10-17:00"]
                    },
                    "max_hours_per_day": 4
                },
                {
                    "name": "Dr. Johnson",
                    "availability": {
                        "MONDAY": ["08:00-17:00"],
                        "TUESDAY": ["08:00-12:00"],
                        "WEDNESDAY": ["08:00-17:00"],
                        "THURSDAY": ["08:00-12:00"],
                        "FRIDAY": ["08:00-13:00", "15:10-17:00"]
                    },
                    "max_hours_per_day": 4
                }
            ]
        }
        
        # Sample classrooms
        classrooms_data = {
            "classrooms": [
                {"name": "A101", "capacity": 50, "is_lab": False, "type": "classroom"},
                {"name": "A102", "capacity": 50, "is_lab": False, "type": "classroom"},
                {"name": "B201", "capacity": 40, "is_lab": True, "type": "lab"},
                {"name": "B202", "capacity": 35, "is_lab": True, "type": "lab"}
            ]
        }
        
        # Sample courses
        courses_data = {
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
                    "is_elective": False,
                    "requires_lab": True
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
                    "is_elective": False,
                    "theory_course_code": "CENG101"
                }
            ]
        }
        
        return instructors_data, classrooms_data, courses_data

