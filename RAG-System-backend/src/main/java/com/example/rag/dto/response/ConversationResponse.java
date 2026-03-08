package com.example.rag.dto.response;

import lombok.*;

@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class ConversationResponse {

    private Long id;
    private String title;
    private String createdAt;
}