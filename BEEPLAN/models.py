"""
Data models for BeePlan scheduling system.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum


class CourseType(Enum):
    THEORY = "theory"
    LAB = "lab"


class Day(Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"


@dataclass
class TimeSlot:
    """Represents a time slot in the schedule."""
    day: Day
    start_time: str  # Format: "HH:MM"
    end_time: str    # Format: "HH:MM"
    
    def overlaps(self, other: 'TimeSlot') -> bool:
        """Check if two time slots overlap."""
        if self.day != other.day:
            return False
        
        def time_to_minutes(time_str: str) -> int:
            h, m = map(int, time_str.split(':'))
            return h * 60 + m
        
        start1 = time_to_minutes(self.start_time)
        end1 = time_to_minutes(self.end_time)
        start2 = time_to_minutes(other.start_time)
        end2 = time_to_minutes(other.end_time)
        
        return not (end1 <= start2 or end2 <= start1)
    
    def __str__(self):
        return f"{self.day.value} {self.start_time}-{self.end_time}"


@dataclass
class Instructor:
    """Represents an instructor."""
    name: str
    availability: Dict[Day, List[str]] = field(default_factory=dict)  # Day -> list of available time slots
    max_hours_per_day: int = 4
    
    def __hash__(self):
        """Make Instructor hashable based on name."""
        return hash(self.name)
    
    def __eq__(self, other):
        """Compare instructors by name."""
        if not isinstance(other, Instructor):
            return False
        return self.name == other.name
    
    def is_available(self, day: Day, time_slot: TimeSlot) -> bool:
        """Check if instructor is available at given time."""
        if day not in self.availability:
            return False
        available_slots = self.availability[day]
        # Check if time slot is within any available slot
        for slot in available_slots:
            if '-' in slot:
                start, end = slot.split('-')
                slot_start = self._time_to_minutes(start.strip())
                slot_end = self._time_to_minutes(end.strip())
                req_start = self._time_to_minutes(time_slot.start_time)
                req_end = self._time_to_minutes(time_slot.end_time)
                if slot_start <= req_start and req_end <= slot_end:
                    return True
        return False
    
    def _time_to_minutes(self, time_str: str) -> int:
        h, m = map(int, time_str.split(':'))
        return h * 60 + m


@dataclass
class Classroom:
    """Represents a classroom or lab."""
    name: str
    capacity: int
    is_lab: bool = False
    type: str = "classroom"  # "classroom" or "lab"
    
    def __hash__(self):
        """Make Classroom hashable based on name."""
        return hash(self.name)
    
    def __eq__(self, other):
        """Compare classrooms by name."""
        if not isinstance(other, Classroom):
            return False
        return self.name == other.name


@dataclass
class Course:
    """Represents a course."""
    code: str
    name: str
    year: int  # 1, 2, 3, or 4
    instructor: Instructor
    course_type: CourseType
    hours_per_week: int
    enrollment: int  # Number of students
    semester: int = 1  # 1 or 2 (Fall/Spring, or First/Second semester)
    department: str = ""  # "CENG", "SENG", etc.
    is_elective: bool = False
    requires_lab: bool = False
    theory_course_code: Optional[str] = None  # For lab courses, link to theory course
    
    def __str__(self):
        return f"{self.code} - {self.name} (Year {self.year}, Semester {self.semester})"


@dataclass
class ScheduledCourse:
    """Represents a course scheduled in a time slot."""
    course: Course
    time_slot: TimeSlot
    classroom: Classroom
    year: int
    semester: int = 1
    
    def __str__(self):
        return f"{self.course.code} @ {self.time_slot} in {self.classroom.name} (Sem {self.semester})"


@dataclass
class Schedule:
    """Represents a complete schedule."""
    scheduled_courses: List[ScheduledCourse] = field(default_factory=list)
    violations: List[str] = field(default_factory=list)
    
    def add_course(self, scheduled_course: ScheduledCourse):
        """Add a scheduled course to the schedule."""
        self.scheduled_courses.append(scheduled_course)
    
    def get_courses_by_year(self, year: int) -> List[ScheduledCourse]:
        """Get all scheduled courses for a specific year."""
        return [sc for sc in self.scheduled_courses if sc.year == year]
    
    def get_courses_by_year_and_semester(self, year: int, semester: int) -> List[ScheduledCourse]:
        """Get all scheduled courses for a specific year and semester."""
        return [sc for sc in self.scheduled_courses if sc.year == year and sc.semester == semester]
    
    def get_courses_by_day(self, day: Day) -> List[ScheduledCourse]:
        """Get all scheduled courses for a specific day."""
        return [sc for sc in self.scheduled_courses if sc.time_slot.day == day]
    
    def get_courses_by_instructor(self, instructor: Instructor) -> List[ScheduledCourse]:
        """Get all scheduled courses for a specific instructor."""
        return [sc for sc in self.scheduled_courses if sc.course.instructor == instructor]

