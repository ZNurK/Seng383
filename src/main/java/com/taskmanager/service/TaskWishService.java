package com.taskmanager.service;

import com.taskmanager.model.*;
import org.springframework.stereotype.Service;
import jakarta.annotation.PostConstruct;
import java.io.*;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.ArrayList;
import java.util.List;

@Service
public class TaskWishService {
    private Child child;
    private Teacher teacher;
    private Parent parent;
    private Operations operations;

    @PostConstruct
    public void init() {
        child = new Child(1123, "Child", 1, 0);
        teacher = new Teacher("Teacher", 123);
        parent = new Parent("Parent", 1213);
        operations = new Operations(teacher, parent, child);
        
        loadTasksFromFile();
        loadWishesFromFile();
    }

    private void loadTasksFromFile() {
        File file1 = new File("Tasks.txt");
        if (!file1.exists()) {
            return;
        }
        try {
            BufferedReader br = new BufferedReader(new FileReader("Tasks.txt"));
            String line;
            while ((line = br.readLine()) != null) {
                if (!line.isEmpty()) {
                    operations.operationselector(inputsplitter(line));
                }
            }
            br.close();
        } catch (IOException e) {
            System.out.println("Error: Unable to open file!");
        }
    }

    private void loadWishesFromFile() {
        File file2 = new File("Wishes.txt");
        if (!file2.exists()) {
            return;
        }
        try {
            BufferedReader br = new BufferedReader(new FileReader("Wishes.txt"));
            String line;
            while ((line = br.readLine()) != null) {
                if (!line.isEmpty()) {
                    operations.operationselector(inputsplitter(line));
                }
            }
        } catch (IOException e) {
            System.out.println("Error: Unable to open file!");
        }
    }

    private List<String> inputsplitter(String in) {
        List<String> prt = new ArrayList<>();
        boolean isWithinQuotes = false;
        StringBuilder sb = new StringBuilder();
        for (char c : in.toCharArray()) {
            if (c == '"') {
                isWithinQuotes = !isWithinQuotes;
            } else if (c == ' ' && !isWithinQuotes) {
                if (!sb.isEmpty()) {
                    prt.add(sb.toString());
                    sb.setLength(0);
                }
            } else {
                sb.append(c);
            }
        }
        if (!sb.isEmpty()) {
            prt.add(sb.toString());
        }
        return prt;
    }

    // Task operations
    public String addTask(String assigner, int taskId, String taskTitle, String taskDescription,
                         String startDate, String startTime, String endDate, String endTime, int coin) {
        List<String> prt = new ArrayList<>();
        prt.add("ADD_TASK");
        prt.add(assigner);
        prt.add(String.valueOf(taskId));
        prt.add(taskTitle);
        prt.add(taskDescription);
        if (startDate != null && !startDate.isEmpty()) prt.add(startDate);
        if (startTime != null && !startTime.isEmpty()) prt.add(startTime);
        if (endDate != null && !endDate.isEmpty()) prt.add(endDate);
        if (endTime != null && !endTime.isEmpty()) prt.add(endTime);
        prt.add(String.valueOf(coin));
        operations.operationselector(prt);
        return "Task added successfully";
    }

    public List<Task> getAllTasks() {
        return child.getAllTasks();
    }

    public List<Task> getDailyTasks() {
        return child.getDailyTasks();
    }

    public List<Task> getWeeklyTasks() {
        return child.getWeeklyTasks();
    }

    public String completeTask(int taskId) {
        child.completeTask(taskId);
        return "Task completed successfully";
    }

    public String checkTask(int taskId, int rating) {
        List<String> prt = new ArrayList<>();
        prt.add("TASK_CHECKED");
        prt.add(String.valueOf(taskId));
        prt.add(String.valueOf(rating));
        operations.operationselector(prt);
        return "Task checked successfully";
    }

    // Wish operations
    public String addWish(String wishId, String wishTitle, String wishDescription,
                         String startDate, String startTime, String endDate, String endTime) {
        List<String> prt = new ArrayList<>();
        prt.add("ADD_WISH");
        prt.add(wishId);
        prt.add(wishTitle);
        prt.add(wishDescription);
        if (startDate != null && !startDate.isEmpty()) prt.add(startDate);
        if (startTime != null && !startTime.isEmpty()) prt.add(startTime);
        if (endDate != null && !endDate.isEmpty()) prt.add(endDate);
        if (endTime != null && !endTime.isEmpty()) prt.add(endTime);
        operations.operationselector(prt);
        return "Wish added successfully";
    }

    public List<Wish> getAllWishes() {
        return child.getAllWishes();
    }

    public String checkWish(String wishID, String status, Integer level) {
        List<String> prt = new ArrayList<>();
        prt.add("WISH_CHECKED");
        prt.add(wishID);
        prt.add(status);
        if (level != null) prt.add(String.valueOf(level));
        operations.operationselector(prt);

        Wish wish = child.getWishByID(wishID);
        if (wish == null) {
            return "Wish not found";
        }

        if ("WAITING".equalsIgnoreCase(wish.getIsApproved())) {
            return "Wish will auto-approve at level " + wish.getLevel();
        }
        return "Wish status: " + wish.getIsApproved();
    }

    // Budget and status
    public int getBudget() {
        return child.getCoins();
    }

    public int getLevel() {
        return child.getLevel();
    }

    public String addCoin(int coin) {
        parent.addCoin(child, coin);
        return coin + " coins added";
    }

    public Child getChild() {
        return child;
    }
}

