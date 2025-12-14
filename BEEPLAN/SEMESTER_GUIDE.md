# Semester Support in BeePlan

BeePlan now supports semester-based scheduling. You can specify which semester (1 or 2) each course belongs to.

## Semester Field

Add a `"semester"` field to each course in your JSON file:

```json
{
  "code": "CENG101",
  "name": "Introduction to Programming",
  "year": 1,
  "semester": 1,
  "instructor": "Dr. Smith",
  "type": "theory",
  "hours_per_week": 3,
  "enrollment": 45
}
```

## Field Details

- **Field Name**: `semester`
- **Type**: integer
- **Required**: No (defaults to 1 if not specified)
- **Valid Values**: `1` or `2`
  - `1` = First semester / Fall semester
  - `2` = Second semester / Spring semester

## How It Works

1. **Scheduling**: Courses from different semesters can be scheduled at the same time (they don't conflict)
2. **Viewing**: Use the semester selector in the timetable to view courses for a specific semester
3. **Conflict Detection**: Only courses in the same year AND semester are checked for student conflicts
4. **Export**: Semester information is included in exported schedules

## Example

```json
{
  "courses": [
    {
      "code": "CENG101",
      "name": "Introduction to Programming",
      "year": 1,
      "semester": 1,
      "instructor": "Dr. Smith",
      "type": "theory",
      "hours_per_week": 3,
      "enrollment": 45
    },
    {
      "code": "CENG102",
      "name": "Data Structures",
      "year": 1,
      "semester": 2,
      "instructor": "Dr. Johnson",
      "type": "theory",
      "hours_per_week": 3,
      "enrollment": 45
    }
  ]
}
```

## Benefits

- ✅ Separate schedules for Fall and Spring semesters
- ✅ Courses from different semesters can share time slots
- ✅ Better organization of academic year
- ✅ Clear separation between semester schedules

## Notes

- If you don't specify `semester`, it defaults to `1`
- Lab courses should have the same semester as their theory course
- The timetable view allows filtering by both year and semester

