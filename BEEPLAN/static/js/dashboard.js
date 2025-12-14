// Dashboard functionality
let currentSchedule = null;
let currentYear = 1;

// File input handler
document.getElementById('dataFile').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        document.getElementById('fileName').textContent = file.name;
        document.getElementById('generateBtn').disabled = false;
    }
});

// Generate schedule
document.getElementById('generateBtn').addEventListener('click', async function() {
    const fileInput = document.getElementById('dataFile');
    const file = fileInput.files[0];
    
    if (!file) {
        showAlert('Please select a data file first', 'error');
        return;
    }
    
    showLoading();
    
    const formData = new FormData();
    formData.append('data', file);
    
    try {
        const response = await fetch('/api/schedule/generate', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            // Handle validation errors
            if (data.validation_errors && Array.isArray(data.validation_errors)) {
                let errorMsg = data.error + ':\n\n';
                data.validation_errors.forEach((err, idx) => {
                    errorMsg += `${idx + 1}. ${err}\n`;
                });
                showValidationErrors(data.validation_errors, data.error);
            } else {
                showAlert(data.error || 'Failed to generate schedule', 'error');
            }
            return;
        }
        
        if (data.success) {
            currentSchedule = data.schedule;
            updateSemesterButtons(); // Update semester buttons based on available data
            showAlert(`Schedule generated successfully! ${data.schedule.scheduled_courses.length} courses scheduled.`, 'success');
            displayTimetable();
            document.getElementById('reportBtn').disabled = false;
            document.getElementById('exportJsonBtn').disabled = false;
            document.getElementById('exportCsvBtn').disabled = false;
        } else {
            showAlert(data.error || 'Failed to generate schedule', 'error');
        }
    } catch (error) {
        showAlert('Error: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
});

// View report
document.getElementById('reportBtn').addEventListener('click', async function() {
    if (!currentSchedule) {
        showAlert('No schedule available', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/report');
        const data = await response.json();
        
        if (data) {
            displayReport(data);
        }
    } catch (error) {
        showAlert('Error loading report: ' + error.message, 'error');
    }
});

// Export functions
document.getElementById('exportJsonBtn').addEventListener('click', function() {
    window.location.href = '/api/schedule/export?format=json';
});

document.getElementById('exportCsvBtn').addEventListener('click', function() {
    window.location.href = '/api/schedule/export?format=csv';
});

// Year selector
document.querySelectorAll('.year-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        document.querySelectorAll('.year-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        currentYear = parseInt(this.dataset.year);
        if (currentSchedule) {
            displayTimetable();
        }
    });
});

// Semester selector (supports 1-8)
let currentSemester = 1;

// Update semester buttons to show only available semesters
function updateSemesterButtons() {
    if (!currentSchedule) return;
    
    // Get all unique semesters from the schedule
    const semesters = new Set();
    if (currentSchedule.scheduled_courses) {
        currentSchedule.scheduled_courses.forEach(sc => {
            if (sc.semester) {
                semesters.add(sc.semester);
            }
        });
    }
    
    // Sort semesters
    const sortedSemesters = Array.from(semesters).sort((a, b) => a - b);
    
    // Hide all semester buttons first
    document.querySelectorAll('.semester-btn').forEach(btn => {
        btn.style.display = 'none';
    });
    
    // Show and update buttons for available semesters
    let hasActive = false;
    sortedSemesters.forEach((sem) => {
        const btn = document.querySelector(`.semester-btn[data-semester="${sem}"]`);
        if (btn) {
            btn.style.display = 'inline-block';
            // Set first available semester as active if current is not available
            if (!sortedSemesters.includes(currentSemester)) {
                if (!hasActive) {
                    currentSemester = sem;
                    btn.classList.add('active');
                    hasActive = true;
                }
            } else if (currentSemester === sem) {
                btn.classList.add('active');
                hasActive = true;
            }
        }
    });
    
    // If no semesters found, show semester 1 by default
    if (sortedSemesters.length === 0) {
        const btn = document.querySelector('.semester-btn[data-semester="1"]');
        if (btn) {
            btn.style.display = 'inline-block';
            btn.classList.add('active');
            currentSemester = 1;
        }
    }
}

// Semester button click handler
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('semester-btn') && e.target.style.display !== 'none') {
        document.querySelectorAll('.semester-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        currentSemester = parseInt(e.target.dataset.semester);
        if (currentSchedule) {
            displayTimetable();
        }
    }
});

// Display timetable
function displayTimetable() {
    if (!currentSchedule) return;
    
    const timetableDiv = document.getElementById('timetable');
    const section = document.getElementById('timetableSection');
    section.style.display = 'block';
    
    // Filter courses by year and semester
    // Convert to numbers to handle potential string/number type mismatches
    const yearCourses = currentSchedule.scheduled_courses.filter(sc => {
        const scYear = parseInt(sc.year);
        const scSemester = parseInt(sc.semester);
        return scYear === currentYear && scSemester === currentSemester;
    });
    
    // Debug logging - show detailed course instance counts
    console.log(`Displaying timetable for Year ${currentYear}, Semester ${currentSemester}`);
    console.log(`Total courses in schedule: ${currentSchedule.scheduled_courses.length}`);
    console.log(`Filtered courses: ${yearCourses.length}`);
    
    // Count instances per course code
    const courseCounts = {};
    yearCourses.forEach(sc => {
        const code = sc.course_code;
        courseCounts[code] = (courseCounts[code] || 0) + 1;
    });
    
    console.log('Course instances in filtered data:');
    Object.keys(courseCounts).sort().forEach(code => {
        console.log(`  ${code}: ${courseCounts[code]} instances`);
    });
    
    if (yearCourses.length > 0) {
        console.log('All filtered courses:', yearCourses.map(sc => ({
            code: sc.course_code,
            day: sc.day,
            time: sc.start_time + '-' + sc.end_time,
            classroom: sc.classroom
        })));
    }
    
    // Create timetable
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
    const timeSlots = [
        { start: '08:00', end: '08:50', row: 0 },
        { start: '09:00', end: '09:50', row: 1 },
        { start: '10:00', end: '10:50', row: 2 },
        { start: '11:00', end: '11:50', row: 3 },
        { start: '12:00', end: '12:50', row: 4 },
        { start: '13:00', end: '13:50', row: 5 },
        { start: '14:00', end: '14:50', row: 6 },
        { start: '15:00', end: '15:50', row: 7 },
        { start: '16:00', end: '16:50', row: 8 }
    ];
    
    let html = '<table class="timetable"><thead><tr><th class="time-header">Time</th>';
    days.forEach(day => {
        html += `<th>${day}</th>`;
    });
    html += '</tr></thead><tbody>';
    
    timeSlots.forEach(timeSlot => {
        html += `<tr><td class="time-header">${timeSlot.start}-${timeSlot.end}</td>`;
        
        days.forEach(day => {
            // Check if Friday and exam block rows (13:00 and 14:00)
            if (day === 'Friday' && (timeSlot.start === '13:00' || timeSlot.start === '14:00')) {
                const label = timeSlot.start === '13:00' ? 'EXAM BLOCK<br>13:20-15:10' : '';
                html += `<td class="course-cell course-exam">${label}</td>`;
            } else {
                // Find courses for this time slot and day
                // Match by exact start time (Friday 15:00 slot uses 15:10 start)
                const courses = yearCourses.filter(sc => {
                    if (sc.day !== day) return false;
                    if (day === 'Friday' && timeSlot.start === '15:00') {
                        return sc.start_time === '15:10';
                    }
                    return sc.start_time === timeSlot.start;
                });
                
                if (courses.length > 0) {
                    // Show all courses at this time slot (should usually be just one for same year/semester)
                    const conflictClass = courses.some(c => hasConflict(c)) ? 'course-conflict' : '';
                    const typeClass = courses[0].course_type === 'lab' ? 'course-lab' : 'course-theory';
                    
                    html += `<td class="course-cell ${typeClass} ${conflictClass}">`;
                    // If multiple courses (shouldn't happen for same year/semester, but handle it)
                    courses.forEach((course, idx) => {
                        if (idx > 0) html += '<br><hr style="margin: 2px 0;">';
                        html += `<strong>${course.course_code}</strong><br>`;
                        html += `${course.classroom}<br>`;
                        html += `<small>${course.instructor}</small>`;
                    });
                    html += '</td>';
                } else {
                    html += '<td></td>';
                }
            }
        });
        
        html += '</tr>';
    });
    
    html += '</tbody></table>';
    
    // Add summary showing course instance counts
    const courseInstanceCounts = {};
    yearCourses.forEach(sc => {
        const code = sc.course_code;
        if (!courseInstanceCounts[code]) {
            courseInstanceCounts[code] = {
                count: 0,
                name: sc.course_name,
                type: sc.course_type
            };
        }
        courseInstanceCounts[code].count++;
    });
    
    let summaryHtml = '<div class="schedule-summary" style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 5px;">';
    summaryHtml += '<h4>Schedule Summary (Year ' + currentYear + ', Semester ' + currentSemester + ')</h4>';
    summaryHtml += '<table style="width: 100%; border-collapse: collapse;">';
    summaryHtml += '<thead><tr><th style="text-align: left; padding: 8px;">Course</th><th style="text-align: left; padding: 8px;">Name</th><th style="text-align: center; padding: 8px;">Scheduled Hours</th><th style="text-align: center; padding: 8px;">Type</th></tr></thead><tbody>';
    
    Object.keys(courseInstanceCounts).sort().forEach(code => {
        const info = courseInstanceCounts[code];
        const typeLabel = info.type === 'lab' ? 'Lab' : 'Theory';
        summaryHtml += `<tr><td style="padding: 8px;"><strong>${code}</strong></td>`;
        summaryHtml += `<td style="padding: 8px;">${info.name}</td>`;
        summaryHtml += `<td style="text-align: center; padding: 8px;"><strong>${info.count}</strong></td>`;
        summaryHtml += `<td style="text-align: center; padding: 8px;">${typeLabel}</td></tr>`;
    });
    
    summaryHtml += '</tbody></table>';
    summaryHtml += '</div>';
    
    timetableDiv.innerHTML = html + summaryHtml;
}

// Check for conflicts
function hasConflict(course) {
    if (!currentSchedule) return false;
    
    for (const other of currentSchedule.scheduled_courses) {
        if (other.course_code === course.course_code) continue;
        
        // Same instructor, same time
        if (other.instructor === course.instructor && 
            other.day === course.day && 
            other.start_time === course.start_time) {
            return true;
        }
        
        // Same classroom, same time
        if (other.classroom === course.classroom && 
            other.day === course.day && 
            other.start_time === course.start_time) {
            return true;
        }
    }
    
    return false;
}

// Display report
function displayReport(data) {
    const reportSection = document.getElementById('reportSection');
    const reportContent = document.getElementById('reportContent');
    
    reportSection.style.display = 'block';
    
    let html = '<div class="report-content">';
    html += `<h4>Schedule Summary</h4>`;
    html += `<p><strong>Total Courses Scheduled:</strong> ${data.total_courses}</p>`;
    
    html += `<h4>Courses by Year</h4><ul>`;
    for (const [year, count] of Object.entries(data.year_counts)) {
        html += `<li>Year ${year}: ${count} courses</li>`;
    }
    html += '</ul>';
    
    if (data.semester_counts) {
        html += `<h4>Courses by Semester</h4><ul>`;
        html += `<li>Semester 1: ${data.semester_counts[1] || 0} courses</li>`;
        html += `<li>Semester 2: ${data.semester_counts[2] || 0} courses</li>`;
        html += '</ul>';
    }
    
    html += `<h4>Schedule Status</h4>`;
    html += `<p class="success">✓ Schedule generated successfully! All conflicts have been automatically resolved.</p>`;
    
    html += '</div>';
    reportContent.innerHTML = html;
    
    // Scroll to report
    reportSection.scrollIntoView({ behavior: 'smooth' });
}

// Show validation errors in a detailed format
function showValidationErrors(errors, title) {
    const container = document.getElementById('alertContainer');
    if (!container) return;
    
    const alert = document.createElement('div');
    alert.className = 'alert alert-error validation-alert';
    alert.style.maxWidth = '600px';
    alert.style.whiteSpace = 'pre-wrap';
    
    let errorText = title + ':\n\n';
    errors.forEach((err, idx) => {
        errorText += `${idx + 1}. ${err}\n`;
    });
    errorText += '\nPlease fix these errors and try again.';
    
    alert.textContent = errorText;
    container.appendChild(alert);
    
    // Scroll to top to show error
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    setTimeout(() => {
        alert.style.animation = 'slideIn 0.3s reverse';
        setTimeout(() => alert.remove(), 300);
    }, 10000); // Show for 10 seconds
}

// Load schedule on page load if available
window.addEventListener('load', async function() {
    try {
        const response = await fetch('/api/schedule/get');
        const data = await response.json();
        
        if (data.success && data.schedule) {
            currentSchedule = data.schedule;
            updateSemesterButtons(); // Update semester buttons based on available data
            displayTimetable();
            document.getElementById('reportBtn').disabled = false;
            document.getElementById('exportJsonBtn').disabled = false;
            document.getElementById('exportCsvBtn').disabled = false;
        }
    } catch (error) {
        // No schedule available, that's okay
    }
});

