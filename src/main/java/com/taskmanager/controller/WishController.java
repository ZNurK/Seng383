package com.taskmanager.controller;

import com.taskmanager.model.Wish;
import com.taskmanager.service.TaskWishService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/wishes")
@CrossOrigin(origins = "*")
public class WishController {

    @Autowired
    private TaskWishService service;

    @PostMapping("/add")
    public Map<String, String> addWish(@RequestBody Map<String, Object> request) {
        String wishId = (String) request.get("wishId");
        String wishTitle = (String) request.get("wishTitle");
        String wishDescription = (String) request.get("wishDescription");
        String startDate = (String) request.get("startDate");
        String startTime = (String) request.get("startTime");
        String endDate = (String) request.get("endDate");
        String endTime = (String) request.get("endTime");
        
        String result = service.addWish(wishId, wishTitle, wishDescription, 
                                        startDate, startTime, endDate, endTime);
        return Map.of("message", result);
    }

    @GetMapping("/all")
    public List<Wish> getAllWishes() {
        return service.getAllWishes();
    }

    @PostMapping("/{wishId}/check")
    public Map<String, String> checkWish(@PathVariable String wishId, @RequestBody Map<String, Object> request) {
        String status = (String) request.get("status");
        Integer level = request.get("level") != null ? Integer.parseInt(request.get("level").toString()) : null;
        String result = service.checkWish(wishId, status, level);
        return Map.of("message", result);
    }
}

