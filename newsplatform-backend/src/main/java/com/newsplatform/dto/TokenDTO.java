package com.newsplatform.dto;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class TokenDTO {
    private Long id;
    private String token;
    private String description;
    private String createdBy;
    private LocalDateTime createdAt;
    private LocalDateTime expiresAt;
    private boolean active;
    private LocalDateTime lastUsedAt;
}
