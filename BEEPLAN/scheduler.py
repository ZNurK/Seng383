"""
Scheduling algorithm for BeePlan.
Implements constraint-based scheduling with backtracking and conflict resolution.
"""
from typing import List, Dict, Optional, Tuple
from models import (
    Course, Instructor, Classroom, Schedule, ScheduledCourse,
    TimeSlot, Day, CourseType
)
import copy
import random


class Scheduler:
    """Main scheduling engine."""
    
    def __init__(self, courses: List[Course], classrooms: List[Classroom], 
                 common_schedule: Optional[Schedule] = None):
        self.courses = courses
        self.classrooms = classrooms
        self.common_schedule = common_schedule or Schedule()
        self.time_slots = self._generate_time_slots()
        self.schedule = Schedule()
        self.violations = []
    
    def _generate_time_slots(self) -> List[TimeSlot]:
        """Generate all possible time slots."""
        time_slots = []
        days = [Day.MONDAY, Day.TUESDAY, Day.WEDNESDAY, Day.THURSDAY, Day.FRIDAY]
        
        # Standard time slots (8:00-17:00, 50-minute periods with 10-minute breaks)
        periods = [
            ("08:00", "08:50"),
            ("09:00", "09:50"),
            ("10:00", "10:50"),
            ("11:00", "11:50"),
            ("12:00", "12:50"),
            ("13:00", "13:50"),
            ("14:00", "14:50"),
            ("15:00", "15:50"),
            ("16:00", "16:50"),
        ]
        
        exam_start = self._time_to_minutes("13:20")
        exam_end = self._time_to_minutes("15:10")
        
        for day in days:
            for start, end in periods:
                if day == Day.FRIDAY:
                    slot_start = self._time_to_minutes(start)
                    slot_end = self._time_to_minutes(end)
                    # Skip slots that overlap the exam block (13:20-15:10)
                    if slot_start < exam_end and slot_end > exam_start:
                        continue
                time_slots.append(TimeSlot(day, start, end))
            
            if day == Day.FRIDAY:
                # Add a custom slot that runs immediately after the exam block
                time_slots.append(TimeSlot(day, "15:10", "16:00"))
        
        return time_slots
    
    def generate_schedule(self) -> Tuple[Schedule, List[str]]:
        """Generate a conflict-free schedule with automatic conflict resolution."""
        # Filter out courses with 0 hours per week
        schedulable_courses = [c for c in self.courses if c.hours_per_week > 0]
        
        # Try multiple scheduling strategies
        strategies = [
            self._strategy_by_year_enrollment,
            self._strategy_by_enrollment,
            self._strategy_by_department,
            self._strategy_random,
        ]
        
        best_schedule = None
        best_scheduled_count = 0
        
        for strategy in strategies:
            self.schedule = Schedule()
            courses_ordered = strategy(schedulable_courses)
            
            # Try to schedule all courses (each course needs hours_per_week instances)
            scheduled_count = 0
            for course in courses_ordered:
                if self._schedule_course_all_hours(course):
                    scheduled_count += 1
            
            # If we scheduled all courses, try to resolve any conflicts
            if scheduled_count == len(courses_ordered):
                self._resolve_conflicts()
                # Check if schedule is now conflict-free
                if len(self._validate_schedule()) == 0:
                    self.schedule.violations = []
                    return self.schedule, []
            
            # Keep track of best schedule
            if scheduled_count > best_scheduled_count:
                best_scheduled_count = scheduled_count
                best_schedule = copy.deepcopy(self.schedule)
        
        # Use best schedule found
        if best_schedule:
            self.schedule = best_schedule
            # Try one more time to resolve conflicts
            self._resolve_conflicts()
        
        # Only report violations if truly impossible
        validation_violations = self._validate_schedule()
        if len(validation_violations) == 0:
            self.schedule.violations = []
        else:
            # Try aggressive conflict resolution
            self._aggressive_conflict_resolution()
            validation_violations = self._validate_schedule()
            self.schedule.violations = validation_violations if validation_violations else []
        
        return self.schedule, self.schedule.violations
    
    def _strategy_by_year_enrollment(self, courses: List[Course]) -> List[Course]:
        """Strategy: Sort by year, then enrollment."""
        theory = [c for c in courses if c.course_type == CourseType.THEORY]
        lab = [c for c in courses if c.course_type == CourseType.LAB]
        theory.sort(key=lambda x: (x.year, -x.enrollment))
        lab.sort(key=lambda x: (x.year, -x.enrollment))
        return theory + lab
    
    def _strategy_by_enrollment(self, courses: List[Course]) -> List[Course]:
        """Strategy: Sort by enrollment (largest first)."""
        theory = [c for c in courses if c.course_type == CourseType.THEORY]
        lab = [c for c in courses if c.course_type == CourseType.LAB]
        theory.sort(key=lambda x: -x.enrollment)
        lab.sort(key=lambda x: -x.enrollment)
        return theory + lab
    
    def _strategy_by_department(self, courses: List[Course]) -> List[Course]:
        """Strategy: Sort by department, then year."""
        theory = [c for c in courses if c.course_type == CourseType.THEORY]
        lab = [c for c in courses if c.course_type == CourseType.LAB]
        theory.sort(key=lambda x: (x.department, x.year, -x.enrollment))
        lab.sort(key=lambda x: (x.department, x.year, -x.enrollment))
        return theory + lab
    
    def _strategy_random(self, courses: List[Course]) -> List[Course]:
        """Strategy: Random order (for diversity)."""
        theory = [c for c in courses if c.course_type == CourseType.THEORY]
        lab = [c for c in courses if c.course_type == CourseType.LAB]
        random.shuffle(theory)
        random.shuffle(lab)
        return theory + lab
    
    def _schedule_course_all_hours(self, course: Course) -> bool:
        """Schedule a course for all its required hours per week."""
        required_hours = course.hours_per_week
        
        if required_hours == 0:
            return True  # Skip courses with 0 hours
        
        # Try multiple strategies to schedule all hours
        for attempt in range(10):  # Try up to 10 times
            scheduled_instances = []
            temp_schedule_backup = copy.deepcopy(self.schedule)
            
            # Try to schedule each hour
            all_scheduled = True
            for hour_num in range(required_hours):
                if not self._schedule_course_instance(course, scheduled_instances):
                    # Failed to schedule this hour, restore and retry
                    self.schedule = temp_schedule_backup
                    all_scheduled = False
                    break
            
            if all_scheduled and len(scheduled_instances) == required_hours:
                # Successfully scheduled all hours
                return True
            
            # Shuffle for next attempt
            random.shuffle(self.time_slots)
        
        # If we couldn't schedule all hours, check if we got at least some
        # Count how many instances are actually scheduled
        actual_count = sum(1 for sc in self.schedule.scheduled_courses 
                          if sc.course.code == course.code)
        return actual_count == required_hours
    
    def _schedule_course_instance(self, course: Course, existing_instances: List[ScheduledCourse]) -> bool:
        """Schedule a single instance of a course (one hour)."""
        # Get available classrooms for this course
        available_classrooms = [
            c for c in self.classrooms
            if (course.course_type == CourseType.LAB and c.is_lab) or
               (course.course_type == CourseType.THEORY and not c.is_lab)
        ]
        
        # Filter by capacity
        available_classrooms = [
            c for c in available_classrooms
            if c.capacity >= course.enrollment
        ]
        
        if not available_classrooms:
            return False
        
        # Shuffle for variety
        time_slots_shuffled = list(self.time_slots)
        random.shuffle(time_slots_shuffled)
        random.shuffle(available_classrooms)
        
        # Try to find a valid time slot
        for time_slot in time_slots_shuffled:
            # Check basic constraints
            if not self._can_schedule_at(course, time_slot):
                continue
            
            # Check if this time slot conflicts with existing instances of the same course
            # (same course shouldn't be scheduled at overlapping times)
            conflicts_with_existing = False
            for existing_instance in existing_instances:
                if existing_instance.time_slot.overlaps(time_slot):
                    conflicts_with_existing = True
                    break
            
            if conflicts_with_existing:
                continue
            
            # Try each available classroom
            for classroom in available_classrooms:
                scheduled = ScheduledCourse(
                    course=course,
                    time_slot=time_slot,
                    classroom=classroom,
                    year=course.year,
                    semester=course.semester
                )
                
                if self._is_valid_placement(scheduled):
                    self.schedule.add_course(scheduled)
                    existing_instances.append(scheduled)
                    return True
        
        return False
    
    def _schedule_course_with_retry(self, course: Course, max_retries: int = 3) -> bool:
        """Schedule a course with retry mechanism (for conflict resolution)."""
        for attempt in range(max_retries):
            if self._schedule_course_instance(course, []):
                return True
            # On retry, shuffle time slots and classrooms for variety
            if attempt < max_retries - 1:
                random.shuffle(self.time_slots)
        return False
    
    def _resolve_conflicts(self):
        """Resolve conflicts by rescheduling conflicting courses."""
        max_iterations = 10
        for iteration in range(max_iterations):
            conflicts = self._find_conflicts()
            if not conflicts:
                break
            
            # Try to reschedule one of the conflicting courses
            for conflict in conflicts[:5]:  # Limit to first 5 conflicts
                course_code = conflict.get('course_code')
                if course_code:
                    # Find and remove all instances of the conflicting course
                    course_instances = [
                        sc for sc in self.schedule.scheduled_courses
                        if sc.course.code == course_code
                    ]
                    if course_instances:
                        # Remove all instances
                        for instance in course_instances:
                            self.schedule.scheduled_courses.remove(instance)
                        # Try to reschedule all hours
                        if not self._schedule_course_all_hours(course_instances[0].course):
                            # Put them back if we can't reschedule
                            for instance in course_instances:
                                self.schedule.add_course(instance)
    
    def _aggressive_conflict_resolution(self):
        """More aggressive conflict resolution by rescheduling multiple courses."""
        max_iterations = 20
        for iteration in range(max_iterations):
            conflicts = self._find_conflicts()
            if not conflicts:
                break
            
            # Get all conflicting courses
            conflicting_courses = set()
            for conflict in conflicts:
                if 'course_code' in conflict:
                    conflicting_courses.add(conflict['course_code'])
                if 'other_course_code' in conflict:
                    conflicting_courses.add(conflict['other_course_code'])
            
            # Remove all conflicting courses (all instances)
            courses_to_reschedule = {}
            for course_code in list(conflicting_courses)[:3]:  # Limit to 3 at a time
                course_instances = [
                    sc for sc in self.schedule.scheduled_courses
                    if sc.course.code == course_code
                ]
                if course_instances:
                    # Remove all instances
                    for instance in course_instances:
                        self.schedule.scheduled_courses.remove(instance)
                    # Store the course to reschedule
                    courses_to_reschedule[course_code] = course_instances[0].course
            
            # Reschedule them (all hours)
            for course in courses_to_reschedule.values():
                self._schedule_course_all_hours(course)
    
    def _find_conflicts(self) -> List[Dict]:
        """Find all conflicts in the current schedule."""
        conflicts = []
        
        # Check instructor overlaps
        instructors = set(sc.course.instructor for sc in self.schedule.scheduled_courses)
        for instructor in instructors:
            instructor_courses = self.schedule.get_courses_by_instructor(instructor)
            for i, sc1 in enumerate(instructor_courses):
                for sc2 in instructor_courses[i+1:]:
                    if sc1.time_slot.overlaps(sc2.time_slot):
                        conflicts.append({
                            'type': 'instructor',
                            'course_code': sc1.course.code,
                            'other_course_code': sc2.course.code
                        })
        
        # Check classroom overlaps
        classrooms = set(sc.classroom for sc in self.schedule.scheduled_courses)
        for classroom in classrooms:
            classroom_courses = [
                sc for sc in self.schedule.scheduled_courses
                if sc.classroom == classroom
            ]
            for i, sc1 in enumerate(classroom_courses):
                for sc2 in classroom_courses[i+1:]:
                    if sc1.time_slot.overlaps(sc2.time_slot):
                        conflicts.append({
                            'type': 'classroom',
                            'course_code': sc1.course.code,
                            'other_course_code': sc2.course.code
                        })
        
        # Check year overlaps (only within same semester)
        # Get all unique year-semester combinations
        year_semester_pairs = set()
        for sc in self.schedule.scheduled_courses:
            year_semester_pairs.add((sc.year, sc.semester))
        
        for year, semester in year_semester_pairs:
            year_semester_courses = self.schedule.get_courses_by_year_and_semester(year, semester)
            for i, sc1 in enumerate(year_semester_courses):
                for sc2 in year_semester_courses[i+1:]:
                    if sc1.time_slot.overlaps(sc2.time_slot):
                        conflicts.append({
                            'type': 'year_semester',
                            'course_code': sc1.course.code,
                            'other_course_code': sc2.course.code
                        })
        
        return conflicts
    
    def _can_schedule_at(self, course: Course, time_slot: TimeSlot) -> bool:
        """Check if a course can be scheduled at a given time slot."""
        # Check Friday exam block
        if time_slot.day == Day.FRIDAY:
            start_minutes = self._time_to_minutes(time_slot.start_time)
            end_minutes = self._time_to_minutes(time_slot.end_time)
            exam_start = self._time_to_minutes("13:20")
            exam_end = self._time_to_minutes("15:10")
            if start_minutes < exam_end and end_minutes > exam_start:
                return False
        
        # Check instructor availability
        if not course.instructor.is_available(time_slot.day, time_slot):
            return False
        
        # Check instructor daily hours limit
        instructor_courses = self.schedule.get_courses_by_instructor(course.instructor)
        day_courses = [sc for sc in instructor_courses if sc.time_slot.day == time_slot.day]
        theory_hours = sum(1 for sc in day_courses if sc.course.course_type == CourseType.THEORY)
        if course.course_type == CourseType.THEORY and theory_hours >= course.instructor.max_hours_per_day:
            return False
        
        # For lab courses, check if theory course is scheduled first
        if course.course_type == CourseType.LAB and course.theory_course_code:
            theory_scheduled = any(
                sc.course.code == course.theory_course_code
                for sc in self.schedule.scheduled_courses
            )
            if not theory_scheduled:
                # Try to find theory course in same day, earlier time
                theory_course = next(
                    (c for c in self.courses if c.code == course.theory_course_code),
                    None
                )
                if theory_course:
                    theory_scheduled_courses = [
                        sc for sc in self.schedule.scheduled_courses
                        if sc.course.code == course.theory_course_code
                    ]
                    if theory_scheduled_courses:
                        theory_time = self._time_to_minutes(
                            theory_scheduled_courses[0].time_slot.start_time
                        )
                        lab_time = self._time_to_minutes(time_slot.start_time)
                        if lab_time <= theory_time:
                            return False
        
        return True
    
    def _is_valid_placement(self, scheduled: ScheduledCourse) -> bool:
        """Check if placing a course at this position is valid."""
        # Check for overlaps with existing courses
        for existing in self.schedule.scheduled_courses:
            # Same instructor, overlapping time
            if (existing.course.instructor == scheduled.course.instructor and
                existing.time_slot.overlaps(scheduled.time_slot)):
                return False
            
            # Same classroom, overlapping time
            if (existing.classroom == scheduled.classroom and
                existing.time_slot.overlaps(scheduled.time_slot)):
                return False
            
            # Same year, overlapping time (students can't be in two places)
            if (existing.year == scheduled.year and
                existing.time_slot.overlaps(scheduled.time_slot)):
                return False
        
        # Check 3rd-year courses vs electives
        if scheduled.course.year == 3:
            for existing in self.schedule.scheduled_courses:
                if (existing.course.is_elective and
                    existing.time_slot.overlaps(scheduled.time_slot)):
                    return False
        
        # Check CENG vs SENG electives
        if scheduled.course.is_elective:
            for existing in self.schedule.scheduled_courses:
                if (existing.course.is_elective and
                    existing.course.department != scheduled.course.department and
                    existing.course.department in ["CENG", "SENG"] and
                    scheduled.course.department in ["CENG", "SENG"] and
                    existing.time_slot.overlaps(scheduled.time_slot)):
                    return False
        
        # Check lab capacity
        if scheduled.course.course_type == CourseType.LAB:
            if scheduled.classroom.capacity > 40:
                return False
        
        return True
    
    def _validate_schedule(self) -> List[str]:
        """Validate the complete schedule and return violations (only critical ones)."""
        violations = []
        
        # Only check for critical violations that prevent scheduling
        # Check instructor overlaps
        instructors = set(sc.course.instructor for sc in self.schedule.scheduled_courses)
        for instructor in instructors:
            instructor_courses = self.schedule.get_courses_by_instructor(instructor)
            for i, sc1 in enumerate(instructor_courses):
                for sc2 in instructor_courses[i+1:]:
                    if sc1.time_slot.overlaps(sc2.time_slot):
                        violations.append(
                            f"Instructor {instructor.name} has overlapping courses: "
                            f"{sc1.course.code} and {sc2.course.code}"
                        )
        
        # Check classroom overlaps
        classrooms = set(sc.classroom for sc in self.schedule.scheduled_courses)
        for classroom in classrooms:
            classroom_courses = [
                sc for sc in self.schedule.scheduled_courses
                if sc.classroom == classroom
            ]
            for i, sc1 in enumerate(classroom_courses):
                for sc2 in classroom_courses[i+1:]:
                    if sc1.time_slot.overlaps(sc2.time_slot):
                        violations.append(
                            f"Classroom {classroom.name} has overlapping courses: "
                            f"{sc1.course.code} and {sc2.course.code}"
                        )
        
        # Check year overlaps (only within same semester)
        # Get all unique year-semester combinations
        year_semester_pairs = set()
        for sc in self.schedule.scheduled_courses:
            year_semester_pairs.add((sc.year, sc.semester))
        
        for year, semester in year_semester_pairs:
            year_semester_courses = self.schedule.get_courses_by_year_and_semester(year, semester)
            for i, sc1 in enumerate(year_semester_courses):
                for sc2 in year_semester_courses[i+1:]:
                    if sc1.time_slot.overlaps(sc2.time_slot):
                        violations.append(
                            f"Year {year} Semester {semester} students have overlapping courses: "
                            f"{sc1.course.code} and {sc2.course.code}"
                        )
        
        return violations
    
    def _time_to_minutes(self, time_str: str) -> int:
        """Convert time string to minutes."""
        h, m = map(int, time_str.split(':'))
        return h * 60 + m

