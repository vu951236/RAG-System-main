package com.example.rag.controller;

import com.example.rag.dto.request.AskRequest;
import com.example.rag.dto.response.UploadResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import com.example.rag.service.RAGService;

@RestController
@RequestMapping("/api/rag")
@RequiredArgsConstructor
public class RAGController {

    private final RAGService service;

    // Upload file
    @PostMapping(
            value = "/upload",
            consumes = MediaType.MULTIPART_FORM_DATA_VALUE
    )
    public UploadResponse upload(
            @RequestPart("file") MultipartFile file
    ) throws Exception {
        return service.upload(file);
    }

    // Ask question -> trả PDF
    @PostMapping(value = "/ask", produces = MediaType.APPLICATION_PDF_VALUE)
    public ResponseEntity<byte[]> ask(
            @RequestBody AskRequest request
    ) throws Exception {

        byte[] pdfBytes = service.askAndGeneratePdf(request);

        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION,
                        "attachment; filename=ket_qua_rag.pdf")
                .contentType(MediaType.APPLICATION_PDF)
                .body(pdfBytes);
    }
}
