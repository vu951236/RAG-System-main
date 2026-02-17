package com.example.rag.dto.response;

import lombok.Data;
import com.fasterxml.jackson.annotation.JsonProperty;

@Data
public class UploadResponse {

    private String status;

    @JsonProperty("total_chunks")
    private Integer totalChunks;
}
