package com.newsplatform.controller;

import com.newsplatform.dto.ArticleDTO;
import com.newsplatform.entity.Article;
import com.newsplatform.entity.Category;
import com.newsplatform.entity.User;
import com.newsplatform.service.ArticleService;
import com.newsplatform.service.CategoryService;
import com.newsplatform.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/articles")
@RequiredArgsConstructor
@CrossOrigin(origins = "http://localhost:3000")
public class ArticleController {

    private final ArticleService articleService;
    private final CategoryService categoryService;
    private final UserService userService;

    @GetMapping("/public")
    public ResponseEntity<Page<ArticleDTO>> getPublishedArticles(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {

        Pageable pageable = PageRequest.of(page, size);
        Page<Article> articles = articleService.getPublishedArticles(pageable);

        Page<ArticleDTO> articleDTOs = articles.map(this::convertToDTO);
        return ResponseEntity.ok(articleDTOs);
    }

    @GetMapping("/public/{id}")
    public ResponseEntity<ArticleDTO> getArticle(@PathVariable Long id) {
        return articleService.getArticleById(id)
                .map(article -> ResponseEntity.ok(convertToDTO(article)))
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/public/category/{categoryId}")
    public ResponseEntity<Page<ArticleDTO>> getArticlesByCategory(
            @PathVariable Long categoryId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {

        Pageable pageable = PageRequest.of(page, size);
        Page<Article> articles = articleService.getArticlesByCategory(categoryId, pageable);

        Page<ArticleDTO> articleDTOs = articles.map(this::convertToDTO);
        return ResponseEntity.ok(articleDTOs);
    }

    @PostMapping("/editor")
    public ResponseEntity<Article> createArticle(
            @RequestBody Article article,
            Authentication authentication) {

        User author = userService.getUserByUsername(authentication.getName())
                .orElseThrow(() -> new RuntimeException("User not found"));

        article.setAuthor(author);

        Category category = categoryService.getCategoryById(article.getCategory().getId())
                .orElseThrow(() -> new RuntimeException("Category not found"));
        article.setCategory(category);

        Article created = articleService.createArticle(article);
        return ResponseEntity.ok(created);
    }

    @PutMapping("/editor/{id}")
    public ResponseEntity<Article> updateArticle(
            @PathVariable Long id,
            @RequestBody Article article) {

        Article updated = articleService.updateArticle(id, article);
        return ResponseEntity.ok(updated);
    }

    @DeleteMapping("/editor/{id}")
    public ResponseEntity<Void> deleteArticle(@PathVariable Long id) {
        articleService.deleteArticle(id);
        return ResponseEntity.noContent().build();
    }

    private ArticleDTO convertToDTO(Article article) {
        ArticleDTO dto = new ArticleDTO();
        dto.setId(article.getId());
        dto.setTitle(article.getTitle());
        dto.setSummary(article.getSummary());
        dto.setContent(article.getContent());
        dto.setCategoryId(article.getCategory().getId());
        dto.setCategoryName(article.getCategory().getName());
        dto.setAuthorName(article.getAuthor().getUsername());
        dto.setPublishedAt(article.getPublishedAt());
        dto.setPublished(article.isPublished());
        dto.setViewCount(article.getViewCount());
        return dto;
    }
}