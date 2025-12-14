# Issues Found in Your JSON File

After analyzing your JSON file, here are the issues that need to be fixed:

## Critical Issues (Must Fix)

### 1. Lab Courses Referencing Themselves

These lab courses have `theory_course_code` pointing to themselves, which is invalid:

- **SENG383** (Software Project III)
  - Current: `"theory_course_code": "SENG383"`
  - Problem: This is a lab course but references itself
  - Fix: Either change it to a theory course, or provide the correct theory course code

- **ELEC_LAB1** (Technical Elective Lab I)
  - Current: `"theory_course_code": "ELEC_LAB1"`
  - Problem: This is a lab course but references itself
  - Fix: Provide the correct theory course code (e.g., if it's for ELEC_TE4, use `"theory_course_code": "ELEC_TE4"`)

- **SENG429** (Enterprise Application Development Laboratory)
  - Current: `"theory_course_code": "SENG429"`
  - Problem: This is a lab course but references itself
  - Fix: Either change it to a theory course, or provide the correct theory course code

## Notes

### Courses with 0 Hours Per Week

These courses will be automatically skipped during scheduling (they won't cause errors):

- **SENG200** (Summer Training I) - `hours_per_week: 0`
- **SENG300** (Summer Training II) - `hours_per_week: 0`

These are likely special courses that don't require weekly scheduling, so they're handled automatically.

## Friday Availability

All instructors correctly avoid the exam block (13:20-15:10) on Fridays. ✅

## Capacity Checks

All course enrollments fit within available classroom/lab capacities. ✅

## How to Fix

1. **For SENG383**: 
   - If it should be a standalone lab, you might need to create a theory course first, or
   - If it's actually a project course, consider if it needs a theory component

2. **For ELEC_LAB1**:
   - Determine which elective theory course this lab belongs to
   - Update `theory_course_code` to that course code (e.g., `"ELEC_TE4"` or `"ELEC_TE5"`)

3. **For SENG429**:
   - If this is a standalone lab, create a corresponding theory course first
   - Or update `theory_course_code` to the correct theory course

## Updated Validation

The system now automatically detects and reports:
- ✅ Lab courses that reference themselves
- ✅ Courses with 0 hours per week (skipped with notification)
- ✅ All other validation rules

After fixing these issues, your JSON file should validate successfully!

