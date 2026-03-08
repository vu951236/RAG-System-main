package com.example.rag.service;

import com.example.rag.dto.request.AskRequest;
import com.example.rag.dto.response.*;
import com.example.rag.entity.ChatHistory;
import com.example.rag.entity.Conversation;
import com.example.rag.entity.User;
import com.example.rag.exception.ApiException;
import com.example.rag.repository.ChatHistoryRepository;
import com.example.rag.repository.ConversationRepository;
import com.example.rag.repository.UserRepository;
import com.lowagie.text.*;
import com.lowagie.text.Font;
import com.lowagie.text.Image;
import com.lowagie.text.pdf.PdfWriter;
import lombok.RequiredArgsConstructor;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.*;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

import java.awt.Color;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.util.Base64;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class RAGService {

    private final RestTemplate restTemplate;
    private final ChatHistoryRepository chatHistoryRepository;
    private final ConversationRepository conversationRepository;
    private final UserRepository userRepository;

    private static final String FASTAPI_BASE = "http://127.0.0.1:8000";

    public Long createNewConversation() {

        User user = getCurrentUser();

        Conversation conversation = Conversation.builder()
                .user(user)
                .title("Cuộc trò chuyện mới")
                .createdAt(LocalDateTime.now())
                .build();

        return conversationRepository.save(conversation).getId();
    }

    public void askInConversation(Long conversationId, AskRequest askRequest) {

        try {

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            HttpEntity<AskRequest> request =
                    new HttpEntity<>(askRequest, headers);

            ResponseEntity<AskResponse> response =
                    restTemplate.postForEntity(
                            FASTAPI_BASE + "/ask",
                            request,
                            AskResponse.class
                    );

            AskResponse result = response.getBody();

            if (result == null) {
                throw new ApiException(
                        "AI không trả dữ liệu",
                        HttpStatus.BAD_GATEWAY
                );
            }

            if (result.getRaw_data() == null || result.getRaw_data().isEmpty()) {
                throw new ApiException(
                        "Chưa upload tài liệu nên không thể truy vấn",
                        HttpStatus.BAD_REQUEST
                );
            }

            if (result.getAnswer() == null || result.getAnswer().trim().isEmpty()) {
                throw new ApiException(
                        "AI chưa trả câu trả lời",
                        HttpStatus.BAD_GATEWAY
                );
            }

            String answer = result.getAnswer().trim();

            if (answer.equalsIgnoreCase("Vui lòng nhập câu hỏi dài hơn 2 từ.")) {
                return;
            }

            byte[] pdfBytes = generatePdf(result);

            String fileName = "rag_" + System.currentTimeMillis() + ".pdf";

            Path path = Paths.get("uploads/pdf/" + fileName);

            Files.createDirectories(path.getParent());

            Files.write(path, pdfBytes);

            saveChatLogic(
                    conversationId,
                    askRequest.getQuestion(),
                    answer,
                    fileName
            );

        } catch (ApiException e) {

            throw e;

        } catch (Exception e) {

            throw new ApiException(
                    "Không thể kết nối tới hệ thống AI",
                    HttpStatus.BAD_GATEWAY
            );

        }

    }

    public List<ConversationResponse> getUserConversations() {

        User user = getCurrentUser();

        return conversationRepository
                .findByUserOrderByCreatedAtDesc(user)
                .stream()
                .map(conv -> ConversationResponse.builder()
                        .id(conv.getId())
                        .title(conv.getTitle())
                        .createdAt(conv.getCreatedAt().toString())
                        .build())
                .collect(Collectors.toList());
    }

    public List<ChatHistoryResponse> getMessagesByConversation(Long conversationId) {

        return chatHistoryRepository
                .findByConversationIdOrderByCreatedAtAsc(conversationId)
                .stream()
                .map(history -> ChatHistoryResponse.builder()
                        .id(history.getId())
                        .question(history.getQuestion())
                        .answer(history.getAnswer())
                        .pdfPath(history.getPdfPath())
                        .createdAt(history.getCreatedAt())
                        .build())
                .collect(Collectors.toList());
    }

    public UploadResponse upload(MultipartFile file) {

        try {

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.MULTIPART_FORM_DATA);

            ByteArrayResource resource =
                    new ByteArrayResource(file.getBytes()) {
                        @Override
                        public String getFilename() {
                            return file.getOriginalFilename();
                        }
                    };

            MultiValueMap<String, Object> body =
                    new LinkedMultiValueMap<>();

            body.add("file", resource);

            HttpEntity<MultiValueMap<String, Object>> request =
                    new HttpEntity<>(body, headers);

            return restTemplate
                    .postForEntity(
                            FASTAPI_BASE + "/upload",
                            request,
                            UploadResponse.class
                    )
                    .getBody();

        } catch (IOException e) {

            throw new ApiException(
                    "Lỗi đọc file",
                    HttpStatus.BAD_REQUEST
            );

        }
    }

    private User getCurrentUser() {

        String username =
                SecurityContextHolder
                        .getContext()
                        .getAuthentication()
                        .getName();

        return userRepository
                .findByUsername(username)
                .orElseThrow(() ->
                        new ApiException(
                                "User not found",
                                HttpStatus.NOT_FOUND
                        )
                );
    }

    private void saveChatLogic(
            Long conversationId,
            String question,
            String answer,
            String pdfPath
    ) {

        Conversation conv =
                conversationRepository
                        .findById(conversationId)
                        .orElseThrow(() ->
                                new ApiException(
                                        "Hội thoại không tồn tại",
                                        HttpStatus.NOT_FOUND
                                )
                        );

        if ("Cuộc trò chuyện mới".equals(conv.getTitle())) {

            String title =
                    question.length() > 50
                            ? question.substring(0, 47) + "..."
                            : question;

            conv.setTitle(title);

            conversationRepository.save(conv);
        }

        ChatHistory history =
                ChatHistory.builder()
                        .user(conv.getUser())
                        .conversation(conv)
                        .question(question)
                        .answer(answer)
                        .pdfPath(pdfPath)
                        .createdAt(LocalDateTime.now())
                        .build();

        chatHistoryRepository.save(history);
    }
    
    private byte[] generatePdf(AskResponse result) {

        try (ByteArrayOutputStream baos =
                     new ByteArrayOutputStream()) {

            Document document =
                    new Document(PageSize.A4, 40, 40, 40, 40);

            PdfWriter.getInstance(document, baos);

            document.open();

            Font titleFont =
                    new Font(Font.HELVETICA, 16, Font.BOLD);

            Font normalFont =
                    new Font(Font.HELVETICA, 12);

            Font boldFont =
                    new Font(Font.HELVETICA, 12, Font.BOLD);

            Font redBoldFont =
                    new Font(Font.HELVETICA, 12, Font.BOLD, Color.RED);

            document.add(new Paragraph(
                    "KẾT QUẢ TRUY XUẤT RAG",
                    titleFont
            ));

            document.add(new Paragraph(" "));

            document.add(new Paragraph(
                    "Câu trả lời:",
                    boldFont
            ));

            document.add(new Paragraph(" "));

            String answer = result.getAnswer();

            answer = answer
                    .replace("<br/>", "\n")
                    .replace("<br>", "\n");

            Pattern highlightPattern =
                    Pattern.compile(
                            "<font color='red'><b>(.*?)</b></font>",
                            Pattern.CASE_INSENSITIVE
                    );

            String[] lines = answer.split("\n");

            for (String line : lines) {

                Paragraph p = new Paragraph();

                Matcher m = highlightPattern.matcher(line);

                int lastEnd = 0;

                while (m.find()) {

                    p.add(new Chunk(
                            line.substring(lastEnd, m.start())
                                    .replaceAll("<.*?>", ""),
                            normalFont
                    ));

                    p.add(new Chunk(
                            m.group(1),
                            redBoldFont
                    ));

                    lastEnd = m.end();
                }

                p.add(new Chunk(
                        line.substring(lastEnd)
                                .replaceAll("<.*?>", ""),
                        normalFont
                ));

                document.add(p);
            }

            if (result.getRaw_data() != null) {

                for (AskResponse.RawData item : result.getRaw_data()) {

                    if (item.getImage_data() != null &&
                            !item.getImage_data().isEmpty()) {

                        document.add(new Paragraph(" "));

                        document.add(new Paragraph(
                                "Ảnh trích xuất từ trang: "
                                        + item.getPage(),
                                boldFont
                        ));

                        byte[] imageBytes =
                                Base64
                                        .getDecoder()
                                        .decode(item.getImage_data().trim());

                        Image img =
                                Image.getInstance(imageBytes);

                        img.scaleToFit(450, 450);

                        img.setAlignment(Image.ALIGN_CENTER);

                        document.add(img);
                    }
                }
            }

            document.close();

            return baos.toByteArray();

        } catch (Exception e) {

            throw new ApiException(
                    "Lỗi PDF: " + e.getMessage(),
                    HttpStatus.INTERNAL_SERVER_ERROR
            );
        }
    }
}