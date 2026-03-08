package com.example.rag.repository;

import com.example.rag.entity.ChatHistory;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface ChatHistoryRepository extends JpaRepository<ChatHistory, Long> {
    List<ChatHistory> findByConversationIdOrderByCreatedAtAsc(Long conversationId);

}