package com.taskmanager.model;

public class Parent extends Adult {
    public Parent(String name, int ID) {
        super(name, ID);
    }

    public void approveWish(Child child, String wishID, String status, Integer requiredLevel) {
        Wish wish = child.getWishByID(wishID);
        if (wish == null) {
            return;
        }

        if (requiredLevel != null && requiredLevel > 0) {
            int sanitized = Math.max(1, requiredLevel);
            wish.setLevel(sanitized);
            requiredLevel = sanitized;
        }

        if ("APPROVED".equalsIgnoreCase(status)) {
            if (requiredLevel != null && child.getLevel() < requiredLevel) {
                wish.setIsApproved("WAITING");
            } else {
                wish.setIsApproved("APPROVED");
            }
        } else {
            wish.setIsApproved(status);
        }
    }
}

