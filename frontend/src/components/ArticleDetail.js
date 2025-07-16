import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Container, Card, Badge, Spinner, Alert } from 'react-bootstrap';
import { getArticle } from '../services/api';

function ArticleDetail() {
  const { id } = useParams();
  const [article, setArticle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadArticle();
  }, [id]);

  const loadArticle = async () => {
    try {
      setLoading(true);
      const response = await getArticle(id);
      setArticle(response.data);
    } catch (err) {
      setError('Erreur lors du chargement de l\'article');
      console.error('Error loading article:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="loading-spinner">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Chargement...</span>
        </Spinner>
      </div>
    );
  }

  if (error) {
    return (
      <Container className="mt-4">
        <Alert variant="danger">{error}</Alert>
        <Link to="/">Retour à l'accueil</Link>
      </Container>
    );
  }

  if (!article) {
    return (
      <Container className="mt-4">
        <Alert variant="warning">Article non trouvé</Alert>
        <Link to="/">Retour à l'accueil</Link>
      </Container>
    );
  }

  return (
    <Container className="mt-4">
      <Link to="/" className="btn btn-link mb-3">
        <i className="fas fa-arrow-left me-2"></i>
        Retour aux articles
      </Link>
      
      <Card>
        <Card.Body>
          <div className="mb-3">
            <Badge bg="secondary" className="me-2">{article.categoryName}</Badge>
            <small className="text-muted">
              <i className="fas fa-eye me-1"></i>
              {article.viewCount} vues
            </small>
          </div>
          
          <h1 className="mb-3">{article.title}</h1>
          
          <div className="text-muted mb-4">
            <small>
              <i className="fas fa-user me-1"></i>
              Par {article.authorName}
              <span className="mx-2">•</span>
              <i className="fas fa-calendar me-1"></i>
              {formatDate(article.publishedAt)}
            </small>
          </div>
          
          {article.summary && (
            <div className="lead mb-4">
              {article.summary}
            </div>
          )}
          
          <hr />
          
          <div 
            className="article-content"
            dangerouslySetInnerHTML={{ __html: article.content }}
          />
        </Card.Body>
      </Card>
    </Container>
  );
}

export default ArticleDetail;