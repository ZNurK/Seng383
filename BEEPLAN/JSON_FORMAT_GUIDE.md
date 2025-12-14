# BeePlan JSON File Format Guide

This guide explains the structure of the JSON file needed for BeePlan course scheduling.

## Complete JSON Structure

The JSON file must contain three main sections: `instructors`, `classrooms`, and `courses`.

```json
{
  "instructors": [...],
  "classrooms": [...],
  "courses": [...]
}
```

---

## 1. Instructors Section

### Structure
```json
{
  "instructors": [
    {
      "name": "Instructor Name",
      "availability": {
        "MONDAY": ["08:00-12:00", "15:00-17:00"],
        "TUESDAY": ["08:00-17:00"],
        "WEDNESDAY": ["08:00-12:00"],
        "THURSDAY": ["08:00-17:00"],
        "FRIDAY": ["08:00-13:00", "15:10-17:00"]
      },
      "max_hours_per_day": 4
    }
  ]
}
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Full name of the instructor (must match course instructor names) |
| `availability` | object | Yes | Available time slots for each day |
| `max_hours_per_day` | integer | No | Maximum theory hours per day (default: 4) |

### Availability Format

- **Day Keys**: Use uppercase day names: `"MONDAY"`, `"TUESDAY"`, `"WEDNESDAY"`, `"THURSDAY"`, `"FRIDAY"`
- **Time Slots**: Array of strings in format `"HH:MM-HH:MM"`
- **Friday Note**: Remember Friday has exam block 13:20-15:10, so avoid that time

### Example
```json
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
}
```

---

## 2. Classrooms Section

### Structure
```json
{
  "classrooms": [
    {
      "name": "Room Name",
      "capacity": 50,
      "is_lab": false,
      "type": "classroom"
    }
  ]
}
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Room identifier (e.g., "A101", "B201") |
| `capacity` | integer | Yes | Maximum number of students |
| `is_lab` | boolean | Yes | `true` for labs, `false` for regular classrooms |
| `type` | string | No | Room type (default: "classroom" or "lab") |

### Important Notes

- **Lab Capacity**: Labs must have capacity ≤ 40 students
- **Lab vs Classroom**: Use `is_lab: true` for lab rooms, `is_lab: false` for theory classrooms

### Example
```json
{
  "classrooms": [
    {"name": "A101", "capacity": 50, "is_lab": false, "type": "classroom"},
    {"name": "A102", "capacity": 50, "is_lab": false, "type": "classroom"},
    {"name": "B201", "capacity": 40, "is_lab": true, "type": "lab"},
    {"name": "B202", "capacity": 35, "is_lab": true, "type": "lab"}
  ]
}
```

---

## 3. Courses Section

### Structure
```json
{
  "courses": [
    {
      "code": "COURSE101",
      "name": "Course Name",
      "year": 1,
      "instructor": "Instructor Name",
      "type": "theory",
      "hours_per_week": 3,
      "enrollment": 45,
      "department": "CENG",
      "is_elective": false,
      "requires_lab": true,
      "theory_course_code": null
    }
  ]
}
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `code` | string | Yes | Unique course code (e.g., "CENG101") |
| `name` | string | Yes | Full course name |
| `year` | integer | Yes | Student year: 1, 2, 3, or 4 |
| `semester` | integer | No | Semester: 1 or 2 (default: 1) |
| `instructor` | string | Yes | Must match an instructor name from instructors section |
| `type` | string | Yes | `"theory"` or `"lab"` |
| `hours_per_week` | integer | No | Hours per week (default: 3) |
| `enrollment` | integer | Yes | Number of enrolled students |
| `department` | string | No | Department code (e.g., "CENG", "SENG") |
| `is_elective` | boolean | No | `true` for electives, `false` for required (default: false) |
| `requires_lab` | boolean | No | For theory courses, indicates if lab exists (default: false) |
| `theory_course_code` | string | No | **For lab courses only**: Code of the theory course this lab belongs to |

### Course Type Rules

#### Theory Courses
```json
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
}
```

#### Lab Courses
```json
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
```

**Important**: Lab courses must have `theory_course_code` pointing to their theory course!

#### Elective Courses
```json
{
  "code": "CENG_E1",
  "name": "Machine Learning",
  "year": 4,
  "instructor": "Dr. Johnson",
  "type": "theory",
  "hours_per_week": 3,
  "enrollment": 25,
  "department": "CENG",
  "is_elective": true,
  "requires_lab": false
}
```

---

## Complete Example

Here's a complete example with all sections:

```json
{
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
  ],
  "classrooms": [
    {"name": "A101", "capacity": 50, "is_lab": false, "type": "classroom"},
    {"name": "A102", "capacity": 50, "is_lab": false, "type": "classroom"},
    {"name": "B201", "capacity": 40, "is_lab": true, "type": "lab"},
    {"name": "B202", "capacity": 35, "is_lab": true, "type": "lab"}
  ],
  "courses": [
    {
      "code": "CENG101",
      "name": "Introduction to Programming",
      "year": 1,
      "semester": 1,
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
      "semester": 1,
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

---

## Automatic Validation

The system automatically validates your data and will show clear error messages if any issues are found. The following rules are automatically enforced:

1. ✅ **Instructor name matching**: The system checks that all course instructors exist in the instructors list
2. ✅ **Lab capacity limit**: Lab rooms must have capacity ≤ 40 (automatically checked)
3. ✅ **Lab course references**: Lab courses must have a valid `theory_course_code` that exists in the courses list
4. ✅ **Friday exam block**: The system prevents scheduling during 13:20-15:10 on Fridays
5. ✅ **Day name format**: Day names must be uppercase (MONDAY, TUESDAY, etc.) - the system will show an error if invalid
6. ✅ **Time format validation**: Time slots must be in 24-hour format (HH:MM-HH:MM) - invalid formats are rejected
7. ✅ **Enrollment vs capacity**: The system ensures course enrollment doesn't exceed available classroom/lab capacity

**Note**: If validation fails, you'll see a detailed list of all errors. Fix them and try again!

---

## Pre-Upload Checklist

Before uploading your JSON file, you can optionally check:

- [ ] JSON is valid (use a JSON validator like jsonlint.com)
- [ ] All required fields are present
- [ ] Data structure matches the format described above

**Note**: The system will automatically validate all business rules when you upload the file. You don't need to manually check the validation rules - the system does it for you!

---

## Quick Reference

### Day Names
- `MONDAY`
- `TUESDAY`
- `WEDNESDAY`
- `THURSDAY`
- `FRIDAY`

### Course Types
- `"theory"` - Theory/lecture courses
- `"lab"` - Laboratory courses

### Years
- `1` - First year
- `2` - Second year
- `3` - Third year
- `4` - Fourth year

### Departments
- `"CENG"` - Computer Engineering
- `"SENG"` - Software Engineering
- Or any custom department code

---

## Need Help?

If you encounter errors when importing:
1. Check the browser console for error messages
2. Validate your JSON using an online JSON validator
3. Ensure all required fields are present
4. Verify instructor names match exactly
5. Check that lab courses reference valid theory courses

