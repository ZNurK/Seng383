package com.taskmanager.controller;

import com.taskmanager.model.Task;
import com.taskmanager.service.TaskWishService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/tasks")
@CrossOrigin(origins = "*")
public class TaskController {

    @Autowired
    private TaskWishService service;

    @PostMapping("/add")
    public Map<String, String> addTask(@RequestBody Map<String, Object> request) {
        String assigner = (String) request.get("assigner");
        int taskId = Integer.parseInt(request.get("taskId").toString());
        String taskTitle = (String) request.get("taskTitle");
        String taskDescription = (String) request.get("taskDescription");
        String startDate = (String) request.get("startDate");
        String startTime = (String) request.get("startTime");
        String endDate = (String) request.get("endDate");
        String endTime = (String) request.get("endTime");
        int coin = Integer.parseInt(request.get("coin").toString());
        
        String result = service.addTask(assigner, taskId, taskTitle, taskDescription, 
                                       startDate, startTime, endDate, endTime, coin);
        return Map.of("message", result);
    }

    @GetMapping("/all")
    public List<Task> getAllTasks() {
        return service.getAllTasks();
    }

    @GetMapping("/daily")
    public List<Task> getDailyTasks() {
        return service.getDailyTasks();
    }

    @GetMapping("/weekly")
    public List<Task> getWeeklyTasks() {
        return service.getWeeklyTasks();
    }

    @PostMapping("/{taskId}/complete")
    public Map<String, String> completeTask(@PathVariable int taskId) {
        String result = service.completeTask(taskId);
        return Map.of("message", result);
    }

    @PostMapping("/{taskId}/check")
    public Map<String, String> checkTask(@PathVariable int taskId, @RequestBody Map<String, Integer> request) {
        int rating = request.get("rating");
        String result = service.checkTask(taskId, rating);
        return Map.of("message", result);
    }
}

