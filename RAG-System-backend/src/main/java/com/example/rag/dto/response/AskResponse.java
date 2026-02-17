package com.example.rag.dto.response;

import lombok.Data;
import java.util.List;

@Data
public class AskResponse {

    private String status;
    private String answer;
    private Integer page;
    private List<RawData> raw_data;

    @Data
    public static class RawData {
        private String text;
        private Integer page;
        private Double score;
        private String image_data;
    }
}
