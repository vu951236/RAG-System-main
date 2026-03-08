package com.example.rag.dto.response;

import lombok.*;
import java.time.LocalDateTime;

@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
public class ChatHistoryResponse {
    private Long id;
    private String question;
    private String answer;
    private String pdfPath;
    private LocalDateTime createdAt;
}