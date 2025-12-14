package com.taskmanager.model;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class Child {
    private int ID;
    private String Name;
    private int level;
    private int coins;
    private List<Task> tasks;
    private List<Wish> wishList;

    public Child(int ID, String Name, int level, int coins) {
        this.ID = ID;
        this.Name = Name;
        this.level = 1;
        this.coins = 0;
        this.tasks = new ArrayList<>();
        this.wishList = new ArrayList<>();
    }

    public void addTask(Task task) {
        tasks.add(task);
        saveTasksToFile("Tasks.txt");
    }

    public void addWish(Wish wish) {
        wishList.add(wish);
        saveWishesToFile("Wishes.txt");
    }

    public void completeTask(int ID) {
        Task task = getTaskbyID(ID);
        if (task != null) {
            task.setCompleted(true);
            saveTasksToFile("Tasks.txt");
        }
    }

    public Task getTaskbyID(int ID) {
        for (Task t : tasks) {
            if (t.getTaskID() == ID) {
                return t;
            }
        }
        return null;
    }

    public Wish getWishByID(String wishID) {
        for (Wish w : wishList) {
            if (w.getWishID().equals(wishID)) {
                return w;
            }
        }
        return null;
    }

    public List<Task> getAllTasks() {
        return new ArrayList<>(tasks);
    }

    public List<Task> getDailyTasks() {
        java.time.LocalDate today = java.time.LocalDate.now();
        List<Task> dailyTasks = new ArrayList<>();
        for (Task t : tasks) {
            if (t.getEnddate() != null && !today.isBefore(t.getEnddate()) &&
                    (t.getStartdate() == null || !today.isBefore(t.getStartdate()))) {
                dailyTasks.add(t);
            }
        }
        return dailyTasks;
    }

    public List<Task> getWeeklyTasks() {
        java.time.LocalDate today = java.time.LocalDate.now();
        java.time.LocalDate Monday = today.minusDays(today.getDayOfWeek().getValue() - 1);
        java.time.LocalDate Sunday = Monday.plusDays(6);
        List<Task> weeklyTasks = new ArrayList<>();
        for (Task t : tasks) {
            if (t.getEnddate() != null && !t.getEnddate().isBefore(Monday) && !t.getEnddate().isAfter(Sunday)) {
                weeklyTasks.add(t);
            }
        }
        return weeklyTasks;
    }

    public List<Wish> getAllWishes() {
        return new ArrayList<>(wishList);
    }

    public void saveTasksToFile(String fileName) {
        try (BufferedWriter bw = new BufferedWriter(new FileWriter(fileName))) {
            for (Task t : tasks) {
                bw.write("ADD_TASK " + t.getAssigner() + " " + t.getTaskID() + " \"" +
                        t.getTaskTitle() + "\" \"" + t.getTaskDescription() + "\" " +
                        (t.getStartdate() != null ? t.getStartdate() + " " : "") +
                        (t.getStartTime() != null ? t.getStartTime() + " " : "") +
                        (t.getEnddate() != null ? t.getEnddate() + " " : "") +
                        (t.getEndTime() != null ? t.getEndTime() + " " : "") +
                        t.getCoin());
                bw.newLine();
            }
        } catch (IOException e) {
            System.out.println("Error: Unable to save tasks to file!");
        }
    }

    public void saveWishesToFile(String fileName) {
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(fileName))) {
            for (Wish w : wishList) {
                writer.write("ADD_WISH " + w.getWishID() + " \"" + w.getWishName() + "\" \"" + w.getWishDescription() + "\" " +
                        (w.getStartdate() != null ? w.getStartdate() + " " : "") +
                        (w.getStartTime() != null ? w.getStartTime() + " " : "") +
                        (w.getEnddate() != null ? w.getEnddate() + " " : "") +
                        (w.getEndTime() != null ? w.getEndTime() + " " : ""));
                writer.newLine();
            }
        } catch (IOException e) {
            System.out.println("Error: Unable to save wishes to file!");
        }
    }

    public int getCoins() {
        return coins;
    }

    public void setCoins(int coins) {
        this.coins = coins;
        updateLevel();
        autoApproveWaitingWishes();
    }

    public int getLevel() {
        return level;
    }

    public List<Task> getTasks() {
        return tasks;
    }

    public void setTasks(List<Task> tasks) {
        this.tasks = tasks;
    }

    public int getID() {
        return ID;
    }

    public String getName() {
        return Name;
    }

    public List<Wish> getWishList() {
        return wishList;
    }

    private void updateLevel() {
        if (coins > 0 && coins <= 40) this.level = 1;
        else if (coins > 40 && coins <= 60) this.level = 2;
        else if (coins > 60 && coins <= 80) this.level = 3;
        else this.level = 4;
    }

    private void autoApproveWaitingWishes() {
        for (Wish wish : wishList) {
            if ("WAITING".equalsIgnoreCase(wish.getIsApproved()) && level >= wish.getLevel()) {
                wish.setIsApproved("APPROVED");
            }
        }
    }
}

