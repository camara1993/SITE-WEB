package com.newsplatform.rest;

import com.newsplatform.dto.ArticleDTO;
import com.newsplatform.entity.Article;
import com.newsplatform.entity.Category;
import com.newsplatform.service.ArticleService;
import com.newsplatform.service.CategoryService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/rest")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class ArticleRestController {

    private final ArticleService articleService;
    private final CategoryService categoryService;

    /**
     * Récupérer la liste de tous les articles publiés
     * Format de retour : XML ou JSON selon l'en-tête Accept
     */
    @GetMapping(value = "/articles",
            produces = {MediaType.APPLICATION_JSON_VALUE, MediaType.APPLICATION_XML_VALUE})
    public ResponseEntity<List<ArticleDTO>> getAllArticles() {
        List<Article> articles = articleService.getAllArticles()
                .stream()
                .filter(Article::isPublished)
                .collect(Collectors.toList());

        List<ArticleDTO> articleDTOs = articles.stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());

        return ResponseEntity.ok(articleDTOs);
    }

    /**
     * Récupérer la liste des articles regroupés par catégories
     * Format de retour : XML ou JSON selon l'en-tête Accept
     */
    @GetMapping(value = "/articles/grouped",
            produces = {MediaType.APPLICATION_JSON_VALUE, MediaType.APPLICATION_XML_VALUE})
    public ResponseEntity<Map<String, List<ArticleDTO>>> getArticlesGroupedByCategory() {
        List<Category> categories = categoryService.getAllCategories();
        Map<String, List<ArticleDTO>> groupedArticles = new HashMap<>();

        for (Category category : categories) {
            List<ArticleDTO> categoryArticles = articleService.getAllArticles()
                    .stream()
                    .filter(article -> article.isPublished() &&
                            article.getCategory().getId().equals(category.getId()))
                    .map(this::convertToDTO)
                    .collect(Collectors.toList());

            if (!categoryArticles.isEmpty()) {
                groupedArticles.put(category.getName(), categoryArticles);
            }
        }

        return ResponseEntity.ok(groupedArticles);
    }

    /**
     * Récupérer la liste des articles appartenant à une catégorie spécifique
     * @param categoryName Le nom de la catégorie
     * Format de retour : XML ou JSON selon l'en-tête Accept
     */
    @GetMapping(value = "/articles/category/{categoryName}",
            produces = {MediaType.APPLICATION_JSON_VALUE, MediaType.APPLICATION_XML_VALUE})
    public ResponseEntity<List<ArticleDTO>> getArticlesByCategory(@PathVariable String categoryName) {
        Category category = categoryService.getCategoryByName(categoryName)
                .orElseThrow(() -> new RuntimeException("Category not found: " + categoryName));

        List<ArticleDTO> articles = articleService.getAllArticles()
                .stream()
                .filter(article -> article.isPublished() &&
                        article.getCategory().getId().equals(category.getId()))
                .map(this::convertToDTO)
                .collect(Collectors.toList());

        return ResponseEntity.ok(articles);
    }

    /**
     * Méthode utilitaire pour convertir une entité Article en DTO
     */
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