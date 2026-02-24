package com.example.rag.controller;

import com.example.rag.dto.request.*;
import com.example.rag.dto.response.LoginResponse;
import com.example.rag.dto.response.MessageResponse;
import com.example.rag.dto.response.RegisterResponse;
import com.example.rag.service.AuthService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    @PostMapping("/register")
    public ResponseEntity<RegisterResponse> register(
            @RequestBody RegisterRequest request
    ) {
        return ResponseEntity.ok(authService.register(request));
    }

    @PostMapping("/verify")
    public ResponseEntity<MessageResponse> verify(
            @RequestBody VerifyOtpRequest request
    ) {
        return ResponseEntity.ok(authService.verify(request));
    }

    @PostMapping("/resend-otp")
    public ResponseEntity<MessageResponse> resendOtp(
            @RequestBody ResendOtpRequest request
    ) {
        return ResponseEntity.ok(authService.resendOtp(request));
    }

    @PostMapping("/login")
    public ResponseEntity<LoginResponse> login(
            @RequestBody LoginRequest request
    ) {
        return ResponseEntity.ok(authService.login(request));
    }
}