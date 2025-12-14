package com.taskmanager.model;

import java.time.LocalDate;
import java.time.LocalTime;

public class Task {
    private int taskID;
    private String taskTitle;
    private String taskDescription;
    private String assigner;
    private LocalDate startdate;
    private LocalTime startTime;
    private LocalDate enddate;
    private LocalTime endTime;
    private int coin;
    private boolean isCompleted;
    private String status;
    private int rating;

    public Task(String assigner, int taskId, String taskTitle, String taskDescription, String startDate, String startTime, String endDate, String endTime, int coin, boolean isCompleted, String status) {
        this.taskID = taskId;
        this.taskTitle = taskTitle;
        this.taskDescription = taskDescription;
        this.assigner = assigner;
        this.startdate = (startDate != null && !startDate.isEmpty()) ? LocalDate.parse(startDate) : null;
        this.startTime = (startTime != null && !startTime.isEmpty()) ? LocalTime.parse(startTime) : null;
        this.enddate = (endDate != null && !endDate.isEmpty()) ? LocalDate.parse(endDate) : null;
        this.endTime = (endTime != null && !endTime.isEmpty()) ? LocalTime.parse(endTime) : null;
        this.coin = coin;
        this.isCompleted = isCompleted;
        this.status = status;
        this.rating = 0;
    }

    public int getTaskID() {
        return taskID;
    }

    public String getTaskTitle() {
        return taskTitle;
    }

    public String getTaskDescription() {
        return taskDescription;
    }

    public String getAssigner() {
        return assigner;
    }

    public int getCoin() {
        return coin;
    }

    public LocalDate getStartdate() {
        return startdate;
    }

    public LocalTime getStartTime() {
        return startTime;
    }

    public LocalDate getEnddate() {
        return enddate;
    }

    public LocalTime getEndTime() {
        return endTime;
    }

    public boolean isCompleted() {
        return isCompleted;
    }

    public String getStatus() {
        return status;
    }

    public int getRating() {
        return rating;
    }

    public void setTaskID(int taskID) {
        this.taskID = taskID;
    }

    public void setTaskTitle(String taskTitle) {
        this.taskTitle = taskTitle;
    }

    public void setTaskDescription(String taskDescription) {
        this.taskDescription = taskDescription;
    }

    public void setAssigner(String assigner) {
        this.assigner = assigner;
    }

    public void setCoin(int coin) {
        this.coin = coin;
    }

    public void setStartdate(LocalDate startdate) {
        this.startdate = startdate;
    }

    public void setStartTime(LocalTime startTime) {
        this.startTime = startTime;
    }

    public void setEnddate(LocalDate enddate) {
        this.enddate = enddate;
    }

    public void setEndTime(LocalTime endTime) {
        this.endTime = endTime;
    }

    public void setCompleted(boolean completed) {
        isCompleted = completed;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public void setRating(int rating) {
        this.rating = rating;
    }
}

