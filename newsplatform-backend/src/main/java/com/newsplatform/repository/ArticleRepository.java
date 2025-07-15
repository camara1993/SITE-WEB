package com.newsplatform.repository;

import com.newsplatform.entity.Article;
import com.newsplatform.entity.Category;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface ArticleRepository extends JpaRepository<Article, Long> {
    Page<Article> findByPublishedTrueOrderByPublishedAtDesc(Pageable pageable);
    Page<Article> findByCategoryAndPublishedTrueOrderByPublishedAtDesc(Category category, Pageable pageable);
    List<Article> findByAuthorIdOrderByCreatedAtDesc(Long authorId);

    @Modifying
    @Query("UPDATE Article a SET a.viewCount = a.viewCount + 1 WHERE a.id = :id")
    void incrementViewCount(@Param("id") Long id);
}