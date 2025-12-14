package com.taskmanager.model;

import java.time.LocalDate;
import java.time.LocalTime;

public class Wish {
    private String wishID;
    private String wishName;
    private String wishDescription;
    private int level;
    private LocalDate startDate;
    private LocalTime startTime;
    private LocalDate endDate;
    private LocalTime endTime;
    private String isApproved;

    public Wish(String wishID, String wishName, String wishDescription, int level, String startDate, String startTime, String endDate, String endTime, String isApproved) {
        this.wishID = wishID;
        this.wishName = wishName;
        this.wishDescription = wishDescription;
        this.level = level;
        this.startDate = (startDate != null && !startDate.isEmpty()) ? LocalDate.parse(startDate) : null;
        this.startTime = (startTime != null && !startTime.isEmpty()) ? LocalTime.parse(startTime) : null;
        this.endDate = (endDate != null && !endDate.isEmpty()) ? LocalDate.parse(endDate) : null;
        this.endTime = (endTime != null && !endTime.isEmpty()) ? LocalTime.parse(endTime) : null;
        this.isApproved = isApproved;
    }

    public String getWishID() {
        return wishID;
    }

    public void setWishID(String wishID) {
        this.wishID = wishID;
    }
    
    public void setIsApproved(String isApproved) {
        this.isApproved = isApproved;
    }

    public String getWishName() {
        return wishName;
    }

    public void setWishName(String wishName) {
        this.wishName = wishName;
    }

    public String getWishDescription() {
        return wishDescription;
    }

    public void setWishDescription(String wishDescription) {
        this.wishDescription = wishDescription;
    }

    public LocalDate getStartdate() {
        return startDate;
    }

    public void setStartdate(LocalDate startdate) {
        this.startDate = startdate;
    }

    public LocalTime getStartTime() {
        return startTime;
    }

    public void setStartTime(LocalTime startTime) {
        this.startTime = startTime;
    }

    public LocalDate getEnddate() {
        return endDate;
    }

    public void setEnddate(LocalDate enddate) {
        this.endDate = enddate;
    }

    public LocalTime getEndTime() {
        return endTime;
    }

    public void setEndTime(LocalTime endTime) {
        this.endTime = endTime;
    }

    public String getIsApproved() {
        return isApproved;
    }

    public void setApproved(String approved) {
        isApproved = approved;
    }

    public int getLevel() {
        return level;
    }

    public void setLevel(int level) {
        this.level = level;
    }
}

