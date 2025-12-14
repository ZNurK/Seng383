"""
PyQt5 GUI for BeePlan scheduling system.
"""
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QTabWidget,
    QLabel, QTextEdit, QFileDialog, QMessageBox, QGroupBox,
    QScrollArea, QGridLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from typing import List, Dict, Optional
from models import Schedule, ScheduledCourse, Day
from scheduler import Scheduler
from data_manager import DataManager


class TimetableWidget(QWidget):
    """Widget for displaying weekly timetable."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.schedule: Optional[Schedule] = None
        self.year: int = 1
        self.semester: int = 1
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        
        # Year and semester selector
        selector_layout = QHBoxLayout()
        
        # Year selector
        selector_layout.addWidget(QLabel("Year:"))
        self.year_buttons = []
        for year in [1, 2, 3, 4]:
            btn = QPushButton(f"Year {year}")
            btn.setCheckable(True)
            if year == 1:
                btn.setChecked(True)
            btn.clicked.connect(lambda checked, y=year: self.set_year(y))
            self.year_buttons.append(btn)
            selector_layout.addWidget(btn)
        
        selector_layout.addSpacing(20)
        
        # Semester selector (1-8 for cumulative semesters)
        selector_layout.addWidget(QLabel("Semester:"))
        self.semester_buttons = []
        for semester in [1, 2, 3, 4, 5, 6, 7, 8]:
            btn = QPushButton(f"Sem {semester}")
            btn.setCheckable(True)
            if semester == 1:
                btn.setChecked(True)
            btn.clicked.connect(lambda checked, s=semester: self.set_semester(s))
            self.semester_buttons.append(btn)
            selector_layout.addWidget(btn)
        
        selector_layout.addStretch()
        layout.addLayout(selector_layout)
        
        # Timetable table
        self.table = QTableWidget()
        self.table.setRowCount(9)  # 9 standard time slots
        self.table.setColumnCount(5)  # 5 days
        
        # Set headers
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        self.table.setHorizontalHeaderLabels(days)
        
        time_slots = [
            "08:00-08:50", "09:00-09:50", "10:00-10:50", "11:00-11:50",
            "12:00-12:50", "13:00-13:50", "14:00-14:50", "15:00-15:50",
            "16:00-16:50"
        ]
        self.table.setVerticalHeaderLabels(time_slots)
        
        # Set table properties
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectItems)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setStretchLastSection(True)
        
        layout.addWidget(self.table)
        self.setLayout(layout)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.schedule: Optional[Schedule] = None
        self.year: int = 1
        self.semester: int = 1
        self.init_ui()
    
    def set_year(self, year: int):
        """Set the year to display."""
        self.year = year
        for i, btn in enumerate(self.year_buttons):
            btn.setChecked(i + 1 == year)
        self.update_timetable()
    
    def set_semester(self, semester: int):
        """Set the semester to display."""
        self.semester = semester
        self.update_timetable()
    
    def set_schedule(self, schedule: Schedule):
        """Set the schedule to display."""
        self.schedule = schedule
        self.update_timetable()
    
    def update_timetable(self):
        """Update the timetable display."""
        # Clear table
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item:
                    item.setText("")
                    item.setBackground(QColor(255, 255, 255))
        
        if not self.schedule:
            return
        
        # Get courses for selected year and semester
        year_courses = self.schedule.get_courses_by_year_and_semester(self.year, self.semester)
        
        # Map time slots to table positions
        time_slot_map = {
            "08:00": 0,
            "09:00": 1,
            "10:00": 2,
            "11:00": 3,
            "12:00": 4,
            "13:00": 5,
            "14:00": 6,
            "15:00": 7,
            "15:10": 7,  # Friday afternoon slot after exam block
            "16:00": 8
        }
        
        day_map = {
            Day.MONDAY: 0, Day.TUESDAY: 1, Day.WEDNESDAY: 2,
            Day.THURSDAY: 3, Day.FRIDAY: 4
        }
        
        # Fill table with scheduled courses
        for sc in year_courses:
            day_col = day_map.get(sc.time_slot.day, -1)
            time_row = time_slot_map.get(sc.time_slot.start_time, -1)
            
            if day_col >= 0 and time_row >= 0:
                item = QTableWidgetItem(
                    f"{sc.course.code}\n{sc.classroom.name}\n{sc.course.instructor.name}"
                )
                
                # Color coding
                if sc.course.course_type.value == "lab":
                    item.setBackground(QColor(173, 216, 230))  # Light blue for labs
                else:
                    item.setBackground(QColor(144, 238, 144))  # Light green for theory
                
                # Check for conflicts (highlight in red)
                if self._has_conflict(sc):
                    item.setBackground(QColor(255, 182, 193))  # Light red for conflicts
                
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(time_row, day_col, item)
        
        # Highlight Friday exam block (between 13:20-15:10) across the 13:00 and 14:00 rows
        exam_block_rows = [5, 6]
        for idx, row in enumerate(exam_block_rows):
            if row >= self.table.rowCount():
                continue
            item = self.table.item(row, 4)  # Friday column
            if not item:
                item = QTableWidgetItem()
                self.table.setItem(row, 4, item)
            if idx == 0:
                item.setText("EXAM BLOCK\n13:20-15:10\n(No Classes)")
            else:
                item.setText("")
            item.setBackground(QColor(255, 255, 200))  # Light yellow
            item.setTextAlignment(Qt.AlignCenter)
    
    def _has_conflict(self, scheduled_course: ScheduledCourse) -> bool:
        """Check if a scheduled course has conflicts."""
        if not self.schedule:
            return False
        
        for sc in self.schedule.scheduled_courses:
            if sc == scheduled_course:
                continue
            
            # Same instructor, overlapping time
            if (sc.course.instructor == scheduled_course.course.instructor and
                sc.time_slot.overlaps(scheduled_course.time_slot)):
                return True
            
            # Same classroom, overlapping time
            if (sc.classroom == scheduled_course.classroom and
                sc.time_slot.overlaps(scheduled_course.time_slot)):
                return True
        
        return False


class ReportWidget(QWidget):
    """Widget for displaying validation reports."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        
        title = QLabel("Validation Report")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        layout.addWidget(self.report_text)
        
        self.setLayout(layout)
    
    def set_report(self, violations: List[str], schedule: Optional[Schedule] = None):
        """Set the report content."""
        report = "=== BEEPLAN SCHEDULE VALIDATION REPORT ===\n\n"
        
        if schedule:
            report += f"Total Scheduled Courses: {len(schedule.scheduled_courses)}\n\n"
            
            # Group by year
            for year in [1, 2, 3, 4]:
                year_courses = schedule.get_courses_by_year(year)
                report += f"Year {year}: {len(year_courses)} courses\n"
            report += "\n"
        
        if violations:
            report += f"VIOLATIONS FOUND: {len(violations)}\n\n"
            for i, violation in enumerate(violations, 1):
                report += f"{i}. {violation}\n"
        else:
            report += "✓ No violations found! Schedule is conflict-free.\n"
        
        self.report_text.setPlainText(report)


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.schedule: Optional[Schedule] = None
        self.courses = []
        self.classrooms = []
        self.instructors: Dict[str, 'Instructor'] = {}
        self.violations = []
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("BeePlan - Course Schedule Generator")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Top buttons
        button_layout = QHBoxLayout()
        
        self.import_btn = QPushButton("Import Data")
        self.import_btn.clicked.connect(self.import_data)
        button_layout.addWidget(self.import_btn)
        
        self.generate_btn = QPushButton("Generate Schedule")
        self.generate_btn.clicked.connect(self.generate_schedule)
        self.generate_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        button_layout.addWidget(self.generate_btn)
        
        self.export_btn = QPushButton("Export Schedule")
        self.export_btn.clicked.connect(self.export_schedule)
        button_layout.addWidget(self.export_btn)
        
        self.view_report_btn = QPushButton("View Report")
        self.view_report_btn.clicked.connect(self.view_report)
        self.view_report_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
        button_layout.addWidget(self.view_report_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Tab widget
        self.tabs = QTabWidget()
        
        # Timetable tab
        self.timetable_widget = TimetableWidget()
        self.tabs.addTab(self.timetable_widget, "Timetable")
        
        # Report tab
        self.report_widget = ReportWidget()
        self.tabs.addTab(self.report_widget, "Report")
        
        layout.addWidget(self.tabs)
        
        # Status bar
        self.statusBar().showMessage("Ready - Import data and generate schedule")
    
    def import_data(self):
        """Import data from JSON files."""
        try:
            # Ask user if they want to import from a single file or separate files
            reply = QMessageBox.question(
                self, "Import Option",
                "Do you want to import from a single combined JSON file?\n\n"
                "Yes: Import all data from one file\n"
                "No: Import from separate files",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Import from single combined file
                file_path, _ = QFileDialog.getOpenFileName(
                    self, "Import All Data", "", "JSON Files (*.json)"
                )
                if file_path:
                    self.instructors, self.classrooms, self.courses = \
                        DataManager.import_all_from_json(file_path)
                    
                    self.statusBar().showMessage(
                        f"Imported: {len(self.courses)} courses, "
                        f"{len(self.classrooms)} classrooms, "
                        f"{len(self.instructors)} instructors"
                    )
                    
                    QMessageBox.information(
                        self, "Import Successful",
                        f"Imported from {file_path}:\n"
                        f"- {len(self.courses)} courses\n"
                        f"- {len(self.classrooms)} classrooms\n"
                        f"- {len(self.instructors)} instructors"
                    )
            else:
                # Import from separate files
                # Import instructors
                instructors_file, _ = QFileDialog.getOpenFileName(
                    self, "Import Instructors", "", "JSON Files (*.json)"
                )
                if instructors_file:
                    self.instructors = DataManager.import_instructors_from_json(instructors_file)
                
                # Import classrooms
                classrooms_file, _ = QFileDialog.getOpenFileName(
                    self, "Import Classrooms", "", "JSON Files (*.json)"
                )
                if classrooms_file:
                    self.classrooms = DataManager.import_classrooms_from_json(classrooms_file)
                
                # Import courses
                courses_file, _ = QFileDialog.getOpenFileName(
                    self, "Import Courses", "", "JSON Files (*.json)"
                )
                if courses_file:
                    self.courses = DataManager.import_courses_from_json(courses_file, self.instructors)
                
                self.statusBar().showMessage(
                    f"Imported: {len(self.courses)} courses, "
                    f"{len(self.classrooms)} classrooms, "
                    f"{len(self.instructors)} instructors"
                )
                
                QMessageBox.information(
                    self, "Import Successful",
                    f"Imported:\n- {len(self.courses)} courses\n"
                    f"- {len(self.classrooms)} classrooms\n"
                    f"- {len(self.instructors)} instructors"
                )
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Error importing data: {str(e)}")
    
    def generate_schedule(self):
        """Generate the schedule."""
        if not self.courses or not self.classrooms:
            QMessageBox.warning(
                self, "Missing Data",
                "Please import courses and classrooms first."
            )
            return
        
        try:
            self.statusBar().showMessage("Generating schedule...")
            QApplication.processEvents()
            
            scheduler = Scheduler(self.courses, self.classrooms)
            self.schedule, self.violations = scheduler.generate_schedule()
            
            # Update timetable
            self.timetable_widget.set_schedule(self.schedule)
            
            # Update report
            self.report_widget.set_report(self.violations, self.schedule)
            
            # Switch to timetable tab
            self.tabs.setCurrentIndex(0)
            
            self.statusBar().showMessage(
                f"Schedule generated: {len(self.schedule.scheduled_courses)} courses scheduled, "
                f"{len(self.violations)} violations"
            )
            
            if self.violations:
                QMessageBox.warning(
                    self, "Schedule Generated",
                    f"Schedule generated with {len(self.violations)} violations. "
                    "Check the Report tab for details."
                )
            else:
                QMessageBox.information(
                    self, "Schedule Generated",
                    "Schedule generated successfully with no violations!"
                )
        except Exception as e:
            QMessageBox.critical(self, "Generation Error", f"Error generating schedule: {str(e)}")
            self.statusBar().showMessage("Error generating schedule")
    
    def export_schedule(self):
        """Export schedule to file."""
        if not self.schedule:
            QMessageBox.warning(self, "No Schedule", "Please generate a schedule first.")
            return
        
        try:
            file_path, selected_filter = QFileDialog.getSaveFileName(
                self, "Export Schedule", "", "JSON Files (*.json);;CSV Files (*.csv)"
            )
            
            if file_path:
                if selected_filter == "JSON Files (*.json)":
                    DataManager.export_schedule_to_json(self.schedule, file_path)
                else:
                    DataManager.export_schedule_to_csv(self.schedule, file_path)
                
                QMessageBox.information(self, "Export Successful", f"Schedule exported to {file_path}")
                self.statusBar().showMessage(f"Schedule exported to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Error exporting schedule: {str(e)}")
    
    def view_report(self):
        """View the validation report."""
        if not self.schedule:
            QMessageBox.warning(self, "No Schedule", "Please generate a schedule first.")
            return
        
        self.report_widget.set_report(self.violations, self.schedule)
        self.tabs.setCurrentIndex(1)  # Switch to report tab


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

