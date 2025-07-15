package com.newsplatform.dto;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ArticleDTO {
    private Long id;
    private String title;
    private String summary;
    private String content;
    private Long categoryId;
    private String categoryName;
    private String authorName;
    private LocalDateTime publishedAt;
    private boolean published;
    private Long viewCount;
}