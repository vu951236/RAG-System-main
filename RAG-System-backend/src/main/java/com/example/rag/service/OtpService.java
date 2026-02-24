package com.example.rag.service;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.security.SecureRandom;

@Service
@RequiredArgsConstructor
public class OtpService {

    private final SecureRandom secureRandom = new SecureRandom();

    public String generateOtp() {
        return String.format("%06d",
                secureRandom.nextInt(1_000_000));
    }
}