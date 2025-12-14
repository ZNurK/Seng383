"""
Script to verify that all courses are scheduled the correct number of times
based on their hours_per_week value.
"""
import json
from collections import defaultdict

def verify_schedule(schedule_file='schedule.json', input_file='test_input.json'):
    """Verify that scheduled courses match hours_per_week requirements."""
    
    # Load input data
    with open(input_file, 'r', encoding='utf-8') as f:
        input_data = json.load(f)
    
    # Create mapping of course codes to hours_per_week
    course_hours = {}
    for course in input_data.get('courses', []):
        course_hours[course['code']] = course.get('hours_per_week', 0)
    
    # Load schedule
    try:
        with open(schedule_file, 'r', encoding='utf-8') as f:
            schedule_data = json.load(f)
    except FileNotFoundError:
        print(f"Schedule file '{schedule_file}' not found.")
        print("Please generate a schedule first.")
        return
    
    # Count scheduled instances per course
    scheduled_counts = defaultdict(int)
    for sc in schedule_data.get('scheduled_courses', []):
        course_code = sc.get('course_code')
        if course_code:
            scheduled_counts[course_code] += 1
    
    # Verify each course
    print("=" * 80)
    print("SCHEDULE VERIFICATION REPORT")
    print("=" * 80)
    print()
    
    issues = []
    correct = []
    skipped = []
    
    for course in input_data.get('courses', []):
        code = course['code']
        name = course['name']
        required_hours = course.get('hours_per_week', 0)
        scheduled_hours = scheduled_counts.get(code, 0)
        
        if required_hours == 0:
            skipped.append((code, name))
        elif scheduled_hours == required_hours:
            correct.append((code, name, required_hours, scheduled_hours))
        else:
            issues.append((code, name, required_hours, scheduled_hours))
    
    # Print results
    if issues:
        print("❌ ISSUES FOUND:")
        print("-" * 80)
        for code, name, required, scheduled in issues:
            print(f"  {code:15} {name:50} Required: {required:2}  Scheduled: {scheduled:2}  ❌")
        print()
    
    if correct:
        print(f"✅ CORRECTLY SCHEDULED ({len(correct)} courses):")
        print("-" * 80)
        for code, name, required, scheduled in correct[:10]:  # Show first 10
            print(f"  {code:15} {name:50} Required: {required:2}  Scheduled: {scheduled:2}  ✅")
        if len(correct) > 10:
            print(f"  ... and {len(correct) - 10} more courses correctly scheduled")
        print()
    
    if skipped:
        print(f"⏭️  SKIPPED (0 hours per week):")
        print("-" * 80)
        for code, name in skipped:
            print(f"  {code:15} {name}")
        print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY:")
    print(f"  Total courses in input: {len(input_data.get('courses', []))}")
    print(f"  Courses with 0 hours (skipped): {len(skipped)}")
    print(f"  Courses correctly scheduled: {len(correct)}")
    print(f"  Courses with issues: {len(issues)}")
    print(f"  Total scheduled instances: {sum(scheduled_counts.values())}")
    print("=" * 80)
    
    if issues:
        print("\n⚠️  WARNING: Some courses are not scheduled correctly!")
        return False
    else:
        print("\n✅ All courses are scheduled correctly!")
        return True

if __name__ == '__main__':
    verify_schedule()

