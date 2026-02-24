package com.example.rag.service;

import com.example.rag.dto.request.AskRequest;
import com.example.rag.dto.response.AskResponse;
import com.example.rag.dto.response.UploadResponse;
import com.example.rag.exception.ApiException;
import com.lowagie.text.*;
import com.lowagie.text.Image;
import com.lowagie.text.pdf.PdfWriter;
import lombok.RequiredArgsConstructor;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

import com.lowagie.text.Font;
import com.lowagie.text.FontFactory;

import java.awt.Color;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.Base64;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import com.lowagie.text.pdf.BaseFont;

@Service
@RequiredArgsConstructor
public class RAGService {

    private final RestTemplate restTemplate;

    private static final String FASTAPI_BASE = "http://127.0.0.1:8000";

    public UploadResponse upload(MultipartFile file) {

        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.MULTIPART_FORM_DATA);

            ByteArrayResource resource = new ByteArrayResource(file.getBytes()) {
                @Override
                public String getFilename() {
                    return file.getOriginalFilename();
                }
            };

            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            body.add("file", resource);

            HttpEntity<MultiValueMap<String, Object>> request =
                    new HttpEntity<>(body, headers);

            ResponseEntity<UploadResponse> response =
                    restTemplate.postForEntity(
                            FASTAPI_BASE + "/upload",
                            request,
                            UploadResponse.class
                    );

            UploadResponse result = response.getBody();

            if (result == null) {
                throw new ApiException(
                        "Không nhận được phản hồi từ hệ thống AI",
                        HttpStatus.BAD_GATEWAY
                );
            }

            return result;

        } catch (IOException e) {
            throw new ApiException(
                    "Không thể đọc file upload",
                    HttpStatus.BAD_REQUEST
            );
        } catch (RestClientException e) {
            throw new ApiException(
                    "Không thể kết nối tới hệ thống AI",
                    HttpStatus.BAD_GATEWAY
            );
        }
    }

    public byte[] askAndGeneratePdf(AskRequest askRequest) {

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
                        "Không nhận được phản hồi từ hệ thống AI",
                        HttpStatus.BAD_GATEWAY
                );
            }

            return generatePdf(result);

        } catch (RestClientException e) {
            throw new ApiException(
                    "Không thể kết nối tới hệ thống AI",
                    HttpStatus.BAD_GATEWAY
            );
        }
    }

    private byte[] generatePdf(AskResponse result) {

        try {
            ByteArrayOutputStream baos = new ByteArrayOutputStream();
            Document document = new Document(PageSize.A4, 40, 40, 40, 40);
            PdfWriter.getInstance(document, baos);
            document.open();

            Font titleFont = new Font(Font.HELVETICA, 16, Font.BOLD);
            Font normalFont = new Font(Font.HELVETICA, 12);
            Font boldFont = new Font(Font.HELVETICA, 12, Font.BOLD);
            Font redBoldFont = new Font(Font.HELVETICA, 12, Font.BOLD, Color.RED);

            // ===== HEADER =====
            document.add(new Paragraph("KẾT QUẢ RAG", titleFont));
            document.add(new Paragraph(" "));
            document.add(new Paragraph("Status: " + result.getStatus(), normalFont));
            document.add(new Paragraph(" "));
            document.add(new Paragraph("Answer:", boldFont));
            document.add(new Paragraph(" "));

            // ===== RENDER ANSWER =====
            String answer = result.getAnswer() == null ? "" : result.getAnswer();
            answer = answer.replace("<br/>", "\n")
                    .replace("<br>", "\n");

            Pattern highlightPattern = Pattern.compile(
                    "<font color='red'><b>(.*?)</b></font>",
                    Pattern.CASE_INSENSITIVE
            );

            String[] lines = answer.split("\n");

            for (String line : lines) {

                Paragraph paragraph = new Paragraph();
                Matcher matcher = highlightPattern.matcher(line);

                int lastEnd = 0;

                while (matcher.find()) {

                    String before = line.substring(lastEnd, matcher.start())
                            .replaceAll("<.*?>", "");
                    paragraph.add(new Chunk(before, normalFont));

                    String highlighted = matcher.group(1);
                    paragraph.add(new Chunk(highlighted, redBoldFont));

                    lastEnd = matcher.end();
                }

                String after = line.substring(lastEnd)
                        .replaceAll("<.*?>", "");
                paragraph.add(new Chunk(after, normalFont));

                document.add(paragraph);
            }

            // ===== IMAGE SECTION =====
            if (result.getRaw_data() != null) {

                for (AskResponse.RawData item : result.getRaw_data()) {

                    if (item.getImage_data() != null &&
                            !item.getImage_data().isEmpty()) {

                        document.add(new Paragraph(" "));
                        document.add(new Paragraph(
                                "Ảnh từ trang " + item.getPage(),
                                boldFont
                        ));
                        document.add(new Paragraph(" "));

                        byte[] imageBytes = Base64.getDecoder()
                                .decode(item.getImage_data().trim());

                        Image image = Image.getInstance(imageBytes);

                        image.scaleToFit(450, 450);
                        image.setAlignment(Image.ALIGN_CENTER);

                        document.add(image);
                    }
                }
            }

            document.close();
            return baos.toByteArray();

        } catch (Exception e) {
            throw new ApiException(
                    "Lỗi khi tạo file PDF: " + e.getMessage(),
                    HttpStatus.INTERNAL_SERVER_ERROR
            );
        }
    }
}