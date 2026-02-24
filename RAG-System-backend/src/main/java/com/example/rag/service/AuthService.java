package com.example.rag.service;

import com.example.rag.dto.request.*;
import com.example.rag.dto.response.LoginResponse;
import com.example.rag.dto.response.MessageResponse;
import com.example.rag.dto.response.RegisterResponse;
import com.example.rag.entity.EmailVerification;
import com.example.rag.entity.User;
import com.example.rag.exception.ApiException;
import com.example.rag.repository.EmailVerificationRepository;
import com.example.rag.repository.UserRepository;
import com.example.rag.security.JwtUtil;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;
    private final EmailVerificationRepository emailVerificationRepository;
    private final PasswordEncoder passwordEncoder;
    private final OtpService otpService;
    private final EmailService emailService;
    private final JwtUtil jwtUtil;

    public RegisterResponse register(RegisterRequest request) {

        if (userRepository.findByUsername(request.getUsername()).isPresent()) {
            throw new ApiException("Username already exists", HttpStatus.BAD_REQUEST);
        }

        if (userRepository.findByEmail(request.getEmail()).isPresent()) {
            throw new ApiException("Email already exists", HttpStatus.BAD_REQUEST);
        }

        User user = User.builder()
                .username(request.getUsername())
                .email(request.getEmail())
                .password(passwordEncoder.encode(request.getPassword()))
                .role("ROLE_USER")
                .enabled(false)
                .createdAt(LocalDateTime.now())
                .build();

        userRepository.save(user);

        emailVerificationRepository.deleteByUser(user);

        String otp = otpService.generateOtp();

        EmailVerification verification = EmailVerification.builder()
                .user(user)
                .otp(otp)
                .expiryTime(LocalDateTime.now().plusMinutes(5))
                .build();

        emailVerificationRepository.save(verification);

        emailService.sendOtpEmail(user.getEmail(), otp);

        return new RegisterResponse(
                "OTP has been sent to your email",
                user.getEmail()
        );
    }

    public MessageResponse verify(VerifyOtpRequest request) {

        User user = userRepository.findByUsername(request.getUsername())
                .orElseThrow(() ->
                        new ApiException("User not found", HttpStatus.NOT_FOUND)
                );

        EmailVerification verification = emailVerificationRepository.findByUser(user)
                .orElseThrow(() ->
                        new ApiException("OTP not found", HttpStatus.BAD_REQUEST)
                );

        if (verification.getExpiryTime().isBefore(LocalDateTime.now())) {
            throw new ApiException("OTP expired", HttpStatus.BAD_REQUEST);
        }

        if (!verification.getOtp().equals(request.getOtp())) {
            throw new ApiException("Invalid OTP", HttpStatus.BAD_REQUEST);
        }

        user.setEnabled(true);
        userRepository.save(user);

        emailVerificationRepository.delete(verification);

        return new MessageResponse("Account verified successfully");
    }

    public MessageResponse resendOtp(ResendOtpRequest request) {

        User user = userRepository.findByUsername(request.getUsername())
                .orElseThrow(() ->
                        new ApiException("User not found", HttpStatus.NOT_FOUND)
                );

        if (user.isEnabled()) {
            throw new ApiException("Account already verified", HttpStatus.BAD_REQUEST);
        }

        EmailVerification existing =
                emailVerificationRepository.findByUser(user).orElse(null);

        if (existing != null) {
            if (existing.getExpiryTime().isAfter(LocalDateTime.now())) {
                throw new ApiException(
                        "OTP still valid. Please check your email.",
                        HttpStatus.BAD_REQUEST
                );
            }
            emailVerificationRepository.delete(existing);
        }

        String otp = otpService.generateOtp();

        EmailVerification newVerification = EmailVerification.builder()
                .user(user)
                .otp(otp)
                .expiryTime(LocalDateTime.now().plusMinutes(5))
                .build();

        emailVerificationRepository.save(newVerification);

        emailService.sendOtpEmail(user.getEmail(), otp);

        return new MessageResponse("New OTP has been sent to your email");
    }

    public LoginResponse login(LoginRequest request) {

        User user = userRepository.findByUsername(request.getUsername())
                .orElseThrow(() ->
                        new ApiException("Invalid credentials", HttpStatus.UNAUTHORIZED)
                );

        if (!user.isEnabled()) {
            throw new ApiException(
                    "Please verify your email first",
                    HttpStatus.FORBIDDEN
            );
        }

        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new ApiException(
                    "Invalid credentials",
                    HttpStatus.UNAUTHORIZED
            );
        }

        String token = jwtUtil.generateToken(user.getUsername());

        return new LoginResponse(
                token,
                user.getUsername(),
                user.getRole()
        );
    }
}