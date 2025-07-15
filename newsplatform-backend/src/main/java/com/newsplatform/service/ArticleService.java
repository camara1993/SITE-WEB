package com.newsplatform.service;

import com.newsplatform.entity.Article;
import com.newsplatform.entity.Category;
import com.newsplatform.repository.ArticleRepository;
import com.newsplatform.repository.CategoryRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
@RequiredArgsConstructor
@Transactional
public class ArticleService {

    private final ArticleRepository articleRepository;
    private final CategoryRepository categoryRepository;

    public Article createArticle(Article article) {
        if (article.isPublished()) {
            article.setPublishedAt(LocalDateTime.now());
        }
        return articleRepository.save(article);
    }

    public Article updateArticle(Long id, Article articleDetails) {
        Article article = articleRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Article not found"));

        article.setTitle(articleDetails.getTitle());
        article.setSummary(articleDetails.getSummary());
        article.setContent(articleDetails.getContent());
        article.setCategory(articleDetails.getCategory());

        if (!article.isPublished() && articleDetails.isPublished()) {
            article.setPublishedAt(LocalDateTime.now());
        }
        article.setPublished(articleDetails.isPublished());

        return articleRepository.save(article);
    }

    public void deleteArticle(Long id) {
        articleRepository.deleteById(id);
    }

    public Optional<Article> getArticleById(Long id) {
        Optional<Article> article = articleRepository.findById(id);
        article.ifPresent(a -> {
            articleRepository.incrementViewCount(a.getId());
        });
        return article;
    }

    public Page<Article> getPublishedArticles(Pageable pageable) {
        return articleRepository.findByPublishedTrueOrderByPublishedAtDesc(pageable);
    }

    public Page<Article> getArticlesByCategory(Long categoryId, Pageable pageable) {
        Category category = categoryRepository.findById(categoryId)
                .orElseThrow(() -> new RuntimeException("Category not found"));
        return articleRepository.findByCategoryAndPublishedTrueOrderByPublishedAtDesc(category, pageable);
    }

    public List<Article> getArticlesByAuthor(Long authorId) {
        return articleRepository.findByAuthorIdOrderByCreatedAtDesc(authorId);
    }

    public List<Article> getAllArticles() {
        return articleRepository.findAll();
    }
}