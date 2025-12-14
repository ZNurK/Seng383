# Task and Wish Management System

This project is a task and wish management system designed for children.  
It has been converted from a GUI-based application into a web-based system.

## Features

- Task creation (by Teacher or Parent)
- Task completion
- Task evaluation and coin rewards
- Wish creation
- Wish approval and rejection
- Automatic wish approval based on level requirements (e.g., Level 3)
- Daily and weekly task listing
- Coin budget and level tracking

## Requirements

- Java 17 or higher
- Maven 3.6 or higher

## Installation and Running

### 1. Clone or Download the Project

### 2. Install Dependencies with Maven

```bash
mvn clean install

3. Run the Application
mvn spring-boot:run


or

java -jar target/task-wish-manager-1.0.0.jar


4. Access the Web Interface

Open your browser and go to:

http://localhost:8080


Usage

Tasks Tab – View, complete, and evaluate tasks

Wishes Tab – View and approve or reject wishes

Add Task Tab – Create new tasks

Add Wish Tab – Create new wishes

API Endpoints
Tasks

GET /api/tasks/all – List all tasks

GET /api/tasks/daily – List daily tasks

GET /api/tasks/weekly – List weekly tasks

POST /api/tasks/add – Add a new task

POST /api/tasks/{taskId}/complete – Complete a task

POST /api/tasks/{taskId}/check – Evaluate a task

Wishes

GET /api/wishes/all – List all wishes

POST /api/wishes/add – Add a new wish

POST /api/wishes/{wishId}/check – Approve or reject a wish

Status

GET /api/status/budget – View budget

GET /api/status/level – View level

POST /api/status/add-coin – Add coins

src/
├── main/
│   ├── java/
│   │   └── com/taskmanager/
│   │       ├── Application.java
│   │       ├── config/
│   │       ├── controller/
│   │       ├── model/
│   │       └── service/
│   └── resources/
│       ├── static/
│       │   ├── index.html
│   │   ├── style.css
│   │   └── app.js
│       └── application.properties
└── pom.xml


Notes

On application startup, data is loaded from Tasks.txt and Wishes.txt if available

All data is stored in memory and automatically written back to files

CORS is enabled for all origins (development purposes)