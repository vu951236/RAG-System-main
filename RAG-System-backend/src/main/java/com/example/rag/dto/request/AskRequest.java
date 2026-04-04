package com.example.rag.dto.request;

import lombok.Data;
import com.fasterxml.jackson.annotation.JsonProperty;

@Data
public class AskRequest {
    @JsonProperty("user_id")
    private String userId;
    @JsonProperty("conversation_id")
    private String conversationId;
    private String question;
}
