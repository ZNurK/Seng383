# BeePlan Web Application

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   python app.py
   ```

3. **Access the Application**
   - Open your browser
   - Navigate to: `http://localhost:5000`
   - Login with: `admin` / `admin123`

## Features

### Authentication
- Secure login system with session management
- Default admin account (change password in production!)
- Session-based authentication

### Dashboard
- Upload course data (JSON format)
- Generate conflict-free schedules
- View validation reports
- Export schedules (JSON/CSV)

### Timetable View
- Interactive weekly timetable
- Color-coded courses:
  - 🟢 Green: Theory courses
  - 🔵 Blue: Lab courses
  - 🔴 Red: Conflicts
  - 🟡 Yellow: Exam block
- Year-based filtering (1st-4th year)

### Validation Report
- Detailed violation list
- Course count by year
- Conflict detection results

## API Endpoints

- `GET /` - Redirect to login or dashboard
- `GET /login` - Login page
- `POST /login` - Authenticate user
- `GET /logout` - Logout user
- `GET /dashboard` - Main dashboard
- `POST /api/schedule/generate` - Generate schedule from uploaded file
- `GET /api/schedule/get` - Get current schedule
- `GET /api/schedule/export` - Export schedule (format: json/csv)
- `GET /api/report` - Get validation report

## Security Notes

⚠️ **For Production Use:**
- Change the `secret_key` in `app.py`
- Use a proper database for user management
- Implement password reset functionality
- Add rate limiting
- Use HTTPS
- Implement proper session management
- Add CSRF protection

## File Upload

The application accepts JSON files with the following structure:
- `instructors` - Array of instructor objects
- `classrooms` - Array of classroom/lab objects
- `courses` - Array of course objects

See `sample_data.json` for a complete example.

## Browser Compatibility

- Chrome/Edge (recommended)
- Firefox
- Safari
- Modern browsers with JavaScript enabled

