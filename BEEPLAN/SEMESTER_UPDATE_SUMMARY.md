# Semester Support Added to BeePlan

## ✅ What's Been Added

### 1. **Data Models Updated**
- `Course` model now includes `semester` field (default: 1)
- `ScheduledCourse` model includes `semester` field
- `Schedule` class has methods to filter by semester

### 2. **Scheduling Logic**
- Courses from different semesters can be scheduled at the same time
- Conflict detection only checks courses in the same year AND semester
- Students can have courses in different semesters at the same time slot

### 3. **User Interface**
- **Web App**: Added semester selector buttons (Semester 1 / Semester 2)
- **Desktop App**: Added semester selector in timetable view
- Timetable filters by both year and semester

### 4. **Data Import/Export**
- JSON import supports `semester` field (defaults to 1 if missing)
- JSON export includes semester information
- CSV export includes semester column

### 5. **Validation**
- Validates semester is 1 or 2
- Ensures semester is an integer

## 📝 JSON Format

Add `"semester": 1` or `"semester": 2` to each course:

```json
{
  "code": "CENG101",
  "name": "Introduction to Programming",
  "year": 1,
  "semester": 1,  // ← Add this field
  "instructor": "Dr. Smith",
  "type": "theory",
  "hours_per_week": 3,
  "enrollment": 45
}
```

## 🎯 How It Works

1. **Scheduling**: 
   - Semester 1 and Semester 2 courses are scheduled independently
   - They can share time slots (no conflict)
   - Only same year + same semester courses conflict

2. **Viewing**:
   - Select Year (1-4) and Semester (1-2) to view specific schedule
   - Timetable shows only courses for selected year and semester

3. **Conflict Detection**:
   - Year 1 Semester 1 courses don't conflict with Year 1 Semester 2 courses
   - Year 1 Semester 1 courses DO conflict with other Year 1 Semester 1 courses

## 📋 Example Structure

```json
{
  "courses": [
    {
      "code": "CENG101",
      "year": 1,
      "semester": 1,  // Fall semester
      ...
    },
    {
      "code": "CENG102",
      "year": 1,
      "semester": 2,  // Spring semester
      ...
    }
  ]
}
```

## ⚠️ Important Notes

- **Default**: If `semester` is not specified, it defaults to `1`
- **Lab Courses**: Should have the same semester as their theory course
- **Backward Compatible**: Existing JSON files without semester will work (defaults to 1)

## 🎨 UI Changes

- **Web**: Semester selector buttons next to year selector
- **Desktop**: Semester selector in timetable widget
- **Report**: Shows course counts by semester

You can now rewrite your test JSON file with semester information!

