# BeePlan Quick Start Guide

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   python main.py
   ```

3. **Import Sample Data**
   - Click "Import Data"
   - Choose "Yes" for single file import
   - Select `sample_data.json`

4. **Generate Schedule**
   - Click "Generate Schedule"
   - View the timetable for different years using the year buttons
   - Click "View Report" to see validation results

5. **Export Schedule**
   - Click "Export Schedule"
   - Choose JSON or CSV format
   - Save to your desired location

## Creating Your Own Data

### Option 1: Single Combined File (Recommended)

Create a JSON file with all three sections:

```json
{
  "instructors": [...],
  "classrooms": [...],
  "courses": [...]
}
```

See `sample_data.json` for a complete example.

### Option 2: Separate Files

Create three separate JSON files:
- `instructors.json` - Contains instructor data
- `classrooms.json` - Contains classroom/lab data  
- `courses.json` - Contains course data

## Time Format

- Use 24-hour format: "HH:MM"
- Time slots are 50 minutes with 10-minute breaks
- Friday exam block: 13:20-15:10 (automatically blocked)

## Tips

- Start with fewer courses to test
- Ensure instructor availability covers all needed time slots
- Make sure lab capacities are ≤ 40 students
- Link lab courses to theory courses using `theory_course_code`

