"""
Generate a summary of all courses and their hours_per_week requirements.
"""
import json
from collections import defaultdict

def analyze_courses(input_file='test_input.json'):
    """Analyze all courses in the input file."""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    courses = data.get('courses', [])
    
    print("=" * 100)
    print("COURSE ANALYSIS - Hours Per Week Summary")
    print("=" * 100)
    print()
    
    # Group by hours_per_week
    by_hours = defaultdict(list)
    by_year = defaultdict(list)
    by_type = defaultdict(list)
    
    total_hours = 0
    schedulable_hours = 0
    
    for course in courses:
        hours = course.get('hours_per_week', 0)
        year = course.get('year', 0)
        course_type = course.get('type', 'unknown')
        code = course.get('code', '')
        name = course.get('name', '')
        
        by_hours[hours].append((code, name, year, course_type))
        by_year[year].append((code, name, hours, course_type))
        by_type[course_type].append((code, name, hours, year))
        
        total_hours += hours
        if hours > 0:
            schedulable_hours += hours
    
    # Print summary by hours
    print("📊 COURSES BY HOURS PER WEEK:")
    print("-" * 100)
    for hours in sorted(by_hours.keys(), reverse=True):
        courses_list = by_hours[hours]
        print(f"\n  {hours} hour(s) per week ({len(courses_list)} courses):")
        for code, name, year, ctype in courses_list:
            print(f"    - {code:15} | {name:50} | Year {year} | {ctype}")
    
    print()
    print("=" * 100)
    print("📊 COURSES BY YEAR:")
    print("-" * 100)
    for year in sorted(by_year.keys()):
        courses_list = by_year[year]
        total_year_hours = sum(h for _, _, h, _ in courses_list)
        print(f"\n  Year {year} ({len(courses_list)} courses, {total_year_hours} total hours):")
        for code, name, hours, ctype in courses_list:
            if hours > 0:
                print(f"    - {code:15} | {name:50} | {hours} hour(s) | {ctype}")
            else:
                print(f"    - {code:15} | {name:50} | SKIPPED (0 hours) | {ctype}")
    
    print()
    print("=" * 100)
    print("📊 SUMMARY STATISTICS:")
    print("-" * 100)
    print(f"  Total courses: {len(courses)}")
    print(f"  Courses with 0 hours (will be skipped): {len(by_hours.get(0, []))}")
    print(f"  Courses to schedule: {len(courses) - len(by_hours.get(0, []))}")
    print(f"  Total hours to schedule: {schedulable_hours}")
    print(f"  Theory courses: {len(by_type.get('theory', []))}")
    print(f"  Lab courses: {len(by_type.get('lab', []))}")
    print()
    print("=" * 100)
    
    # Expected schedule instances
    print("\n📋 EXPECTED SCHEDULE INSTANCES:")
    print("-" * 100)
    print("Each course should appear in the schedule the following number of times:")
    print()
    for hours in sorted(by_hours.keys(), reverse=True):
        if hours == 0:
            continue
        courses_list = by_hours[hours]
        print(f"  {hours} instance(s): {len(courses_list)} courses")
        for code, name, _, _ in courses_list[:5]:  # Show first 5
            print(f"    - {code}: {name}")
        if len(courses_list) > 5:
            print(f"    ... and {len(courses_list) - 5} more")
    print()
    print("=" * 100)

if __name__ == '__main__':
    analyze_courses()

