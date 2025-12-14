# Automatic Data Validation

BeePlan now includes comprehensive automatic validation that checks your data before scheduling. You no longer need to manually verify these rules - the system does it for you!

## Validation Rules

The system automatically validates the following:

### 1. Instructor Validation
- ✅ All instructor names are unique
- ✅ All instructors have availability specified
- ✅ Day names are valid (MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY)
- ✅ Time slots are in correct format (HH:MM-HH:MM, 24-hour)
- ✅ Friday availability doesn't overlap with exam block (13:20-15:10)

### 2. Classroom Validation
- ✅ All classroom names are unique
- ✅ All classrooms have valid capacity (positive integer)
- ✅ Lab rooms have capacity ≤ 40 students
- ✅ Classroom types are correctly specified (lab vs classroom)

### 3. Course Validation
- ✅ All course codes are unique
- ✅ All course instructors exist in the instructors list
- ✅ Course types are valid ("theory" or "lab")
- ✅ Lab courses have `theory_course_code` that references an existing theory course
- ✅ Course enrollment is a positive integer
- ✅ Course enrollment doesn't exceed available classroom/lab capacity

### 4. Cross-Validation
- ✅ Course instructor names match instructor names exactly
- ✅ Lab courses reference valid theory courses
- ✅ Suitable classrooms/labs exist for each course type
- ✅ Enrollment fits within available capacity

## Error Messages

When validation fails, you'll see:
- A clear error message explaining what went wrong
- A numbered list of all validation errors
- Specific details about which field/course/instructor has the problem
- Suggestions on how to fix the errors

## Example Error Output

```
Data validation failed:

1. Course 'CENG101': Instructor 'Dr. Unknown' not found in instructors list. Available instructors: Dr. Smith, Dr. Johnson
2. Lab 'B201': Capacity 50 exceeds maximum of 40 students
3. Lab course 'CENG101L': Theory course 'CENG100' not found in courses list
4. Course 'CENG102': Enrollment 60 exceeds maximum classroom capacity of 50
5. Instructor 'Dr. Smith': Friday availability '13:00-15:00' overlaps with exam block (13:20-15:10)
```

## How It Works

1. **Upload your JSON file** - The system reads your data
2. **Automatic validation** - All rules are checked immediately
3. **Clear feedback** - If errors exist, you see exactly what's wrong
4. **Fix and retry** - Correct the errors and upload again
5. **Schedule generation** - Once validation passes, scheduling proceeds

## Benefits

- ✅ **No manual checking required** - The system validates everything
- ✅ **Clear error messages** - Know exactly what to fix
- ✅ **Prevents scheduling errors** - Catch problems before scheduling
- ✅ **Saves time** - Fix issues upfront instead of during scheduling
- ✅ **Better data quality** - Ensures consistent, valid data

## Technical Details

Validation is performed by the `DataValidator` class in `data_manager.py`:
- `validate_instructors()` - Validates instructor data
- `validate_classrooms()` - Validates classroom/lab data
- `validate_courses()` - Validates course data
- `validate_enrollment_vs_capacity()` - Cross-validates enrollment and capacity
- `validate_all()` - Runs all validations

All validation happens before any scheduling logic runs, ensuring only valid data enters the scheduling system.

