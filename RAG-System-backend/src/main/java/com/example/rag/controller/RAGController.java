package com.example.rag.controller;

import com.example.rag.dto.request.AskRequest;
import com.example.rag.dto.response.ChatHistoryResponse;
import com.example.rag.dto.response.ConversationResponse;
import com.example.rag.dto.response.UploadResponse;
import com.example.rag.entity.Conversation;
import com.example.rag.service.RAGService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

@RestController
@RequestMapping("/api/rag")
@RequiredArgsConstructor
public class RAGController {

    private final RAGService service;

    @PostMapping("/conversation/new")
    public ResponseEntity<Long> createNewConversation() {
        return ResponseEntity.ok(service.createNewConversation());
    }

    @GetMapping("/conversations")
    public ResponseEntity<List<ConversationResponse>> getConversations() {
        return ResponseEntity.ok(service.getUserConversations());
    }

    @GetMapping("/conversation/{id}/messages")
    public ResponseEntity<List<ChatHistoryResponse>> getMessages(@PathVariable Long id) {
        return ResponseEntity.ok(service.getMessagesByConversation(id));
    }

    @PostMapping("/conversation/{id}/ask")
    public ResponseEntity<Void> ask(
            @PathVariable Long id,
            @RequestBody AskRequest request
    ) {

        service.askInConversation(id, request);

        return ResponseEntity.ok().build();
    }

    @PostMapping(value = "/upload", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<UploadResponse> upload(@RequestPart("file") MultipartFile file) {
        return ResponseEntity.ok(service.upload(file));
    }
}