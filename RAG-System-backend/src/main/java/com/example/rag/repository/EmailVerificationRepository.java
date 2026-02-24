package com.example.rag.repository;

import com.example.rag.entity.EmailVerification;
import com.example.rag.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface EmailVerificationRepository
        extends JpaRepository<EmailVerification, Long> {

    Optional<EmailVerification> findByUser(User user);

    void deleteByUser(User user);
}