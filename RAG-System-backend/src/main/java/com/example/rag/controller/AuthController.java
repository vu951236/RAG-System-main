package com.example.rag.controller;

import com.example.rag.dto.request.LoginRequest;
import com.example.rag.security.JwtUtil;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final JwtUtil jwtUtil;

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody LoginRequest request) {

        // Hardcode demo
        if ("admin".equals(request.getUsername())
                && "123456".equals(request.getPassword())) {

            String token = jwtUtil.generateToken(request.getUsername());
            return ResponseEntity.ok(token);
        }

        return ResponseEntity.status(401).body("Sai tài khoản hoặc mật khẩu");
    }
}