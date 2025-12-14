package com.taskmanager.controller;

import com.taskmanager.service.TaskWishService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import java.util.Map;

@RestController
@RequestMapping("/api/status")
@CrossOrigin(origins = "*")
public class StatusController {

    @Autowired
    private TaskWishService service;

    @GetMapping("/budget")
    public Map<String, Integer> getBudget() {
        return Map.of("budget", service.getBudget());
    }

    @GetMapping("/level")
    public Map<String, Integer> getLevel() {
        return Map.of("level", service.getLevel());
    }

    @PostMapping("/add-coin")
    public Map<String, String> addCoin(@RequestBody Map<String, Integer> request) {
        int coin = request.get("coin");
        String result = service.addCoin(coin);
        return Map.of("message", result);
    }
}

