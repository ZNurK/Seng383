package com.taskmanager.service;

import com.taskmanager.model.*;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.List;

public class Operations {
    private Teacher teacher;
    private Parent parent;
    private Child child;

    public Operations(Teacher teacher, Parent parent, Child child) {
        this.teacher = teacher;
        this.parent = parent;
        this.child = child;
    }

    public void operationselector(List<String> prt) {
        if (prt == null || prt.isEmpty()) {
            return;
        }

        String op = prt.get(0);

        if (op.startsWith("ADD_TASK")) {
            operationAddTask(prt);
        } else if (op.equalsIgnoreCase("LIST_ALL_TASKS")) {
            // Handled in service
        } else if (op.equalsIgnoreCase("TASK_CHECKED")) {
            operationCheckTask(prt);
        } else if (op.equalsIgnoreCase("TASK_DONE")) {
            operationCompleteTask(prt);
        } else if (op.startsWith("ADD_WISH")) {
            operationAddWish(prt);
        } else if (op.equalsIgnoreCase("LIST_ALL_WISHES")) {
            // Handled in service
        } else if (op.equalsIgnoreCase("ADD_BUDGET_COIN")) {
            operationAddCoin(prt);
        } else if (op.equalsIgnoreCase("WISH_CHECKED")) {
            operationCheckWish(prt);
        } else if (op.equalsIgnoreCase("PRINT_BUDGET")) {
            // Handled in service
        } else if (op.equalsIgnoreCase("PRINT_STATUS")) {
            // Handled in service
        }
    }

    private void operationCheckWish(List<String> prt) {
        if (prt.size() < 3) {
            return;
        }

        String wishID = prt.get(1);
        String status = prt.get(2).toUpperCase();
        Integer requiredLevel = null;
        if (prt.size() == 4) {
            try {
                requiredLevel = Integer.parseInt(prt.get(3));
            } catch (NumberFormatException e) {
                System.out.println("Invalid level requirement for wish: " + prt.get(3));
                return;
            }
        }

        if (status.equals("APPROVED")) {
            parent.approveWish(child, wishID, "APPROVED", requiredLevel);
        } else if (status.equals("REJECTED")) {
            parent.approveWish(child, wishID, "REJECTED", null);
        }
    }

    private void operationAddCoin(List<String> prt) {
        if (prt.size() == 2) {
            int coin = Integer.parseInt(prt.get(1));
            parent.addCoin(child, coin);
        }
    }

    public void operationAddWish(List<String> prt) {
        if (prt.size() < 4) {
            return;
        }

        String wishId = prt.get(1).trim();
        String wishTitle = prt.get(2).trim();
        String wishDescription = prt.get(3).trim();

        String startDate = null, endDate = null, startTime = null, endTime = null;
        int i = 4;

        while (i < prt.size()) {
            String data = prt.get(i);

            if (isDate(data)) {
                if (endDate == null) {
                    endDate = data;
                } else if (startDate == null) {
                    startDate = endDate;
                    endDate = data;
                }
            } else if (isTime(data)) {
                if (endTime == null && endDate != null) {
                    endTime = data;
                } else if (startTime == null && startDate != null) {
                    startTime = endTime;
                    endTime = data;
                }
            }
            i++;
        }

        Wish wish = new Wish(wishId, wishTitle, wishDescription, child.getLevel(), startDate, startTime, endDate, endTime, "PENDING");
        child.addWish(wish);
    }

    private void operationCompleteTask(List<String> prt) {
        if (prt.size() == 2) {
            int taskId;
            try {
                taskId = Integer.parseInt(prt.get(1));
            } catch (NumberFormatException e) {
                return;
            }
            child.completeTask(taskId);
        }
    }

    private void operationCheckTask(List<String> prt) {
        if (prt.size() == 3) {
            int taskId;
            int rating;
            try {
                taskId = Integer.parseInt(prt.get(1));
                rating = Integer.parseInt(prt.get(2));
            } catch (NumberFormatException e) {
                return;
            }

            if (rating < 1 || rating > 5) {
                return;
            }

            Task task = child.getTaskbyID(taskId);
            if (task == null) {
                return;
            }

            if (!task.isCompleted()) {
                return;
            }

            if (task.getAssigner().equalsIgnoreCase("T")) {
                teacher.checkTask(task, rating, child);
            } else {
                parent.checkTask(task, rating, child);
            }
        }
    }

    public void operationAddTask(List<String> prt) {
        if (prt.size() < 6) {
            return;
        }

        String assigner = prt.get(1);
        if (!assigner.equalsIgnoreCase("P") && !assigner.equalsIgnoreCase("T")) {
            return;
        }

        int taskId;
        try {
            taskId = Integer.parseInt(prt.get(2));
        } catch (NumberFormatException e) {
            return;
        }

        String taskTitle = prt.get(3).trim();
        String taskDescription = prt.get(4).trim();

        String startDate = null, endDate = null, startTime = null, endTime = null;
        int i = 5;

        while (i < prt.size() - 1) {
            String data = prt.get(i);

            if (isDate(data)) {
                if (endDate == null) {
                    endDate = data;
                } else if (startDate == null) {
                    startDate = endDate;
                    endDate = data;
                }
            } else if (isTime(data)) {
                if (endTime == null && endDate != null) {
                    endTime = data;
                } else if (startTime == null && startDate != null) {
                    startTime = endTime;
                    endTime = data;
                }
            }
            i++;
        }

        int coin;
        try {
            coin = Integer.parseInt(prt.get(prt.size() - 1));
            if (coin < 0) {
                return;
            }
        } catch (NumberFormatException e) {
            return;
        }

        Task task = new Task(assigner, taskId, taskTitle, taskDescription, startDate, startTime, endDate, endTime, coin, false, "Pending");

        if (assigner.equalsIgnoreCase("T")) {
            teacher.addTask(child, task);
        } else {
            parent.addTask(child, task);
        }
    }

    public boolean isDate(String dateStr) {
        try {
            DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd");
            LocalDate.parse(dateStr, formatter);
            return true;
        } catch (DateTimeParseException e) {
            return false;
        }
    }

    public boolean isTime(String timeStr) {
        return timeStr.matches("([01]\\d|2[0-3]):[0-5]\\d");
    }
}

