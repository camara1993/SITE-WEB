import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Card, Row, Col, Pagination, Badge, Container, Breadcrumb } from 'react-bootstrap';
import { getArticlesByCategory, getCategories } from '../services/api';
import { toast } from 'react-toastify';

function CategoryList() {
  const { id } = useParams();
  const [articles, setArticles] = useState([]);
  const [category, setCategory] = useState(null);
  const [currentPage, setCurrentPage] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCategoryAndArticles();
  }, [id, currentPage]);

  const loadCategoryAndArticles = async () => {
    try {
      setLoading(true);
      
      // Charger les informations de la catégorie
      const categoriesResponse = await getCategories();
      const currentCategory = categoriesResponse.data.find(cat => cat.id === parseInt(id));
      setCategory(currentCategory);
      
      // Charger les articles
      const response = await getArticlesByCategory(id, currentPage, 6);
      setArticles(response.data.content);
      setTotalPages(response.data.totalPages);
    } catch (error) {
      toast.error('Erreur lors du chargement des articles');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  if (loading) {
    return (
      <div className="text-center mt-5">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Chargement...</span>
        </div>
      </div>
    );
  }

  return (
    <Container className="mt-4">
      <Breadcrumb>
        <Breadcrumb.Item linkAs={Link} linkProps={{ to: "/" }}>
          Accueil
        </Breadcrumb.Item>
        <Breadcrumb.Item active>
          {category ? category.name : 'Catégorie'}
        </Breadcrumb.Item>
      </Breadcrumb>

      <h1 className="mb-4">
        {category && (
          <>
            Articles - {category.name}
            {category.description && (
              <p className="lead mt-2">{category.description}</p>
            )}
          </>
        )}
      </h1>
      
      {articles.length === 0 ? (
        <div className="alert alert-info">
          Aucun article dans cette catégorie pour le moment.
        </div>
      ) : (
        <>
          <Row>
            {articles.map(article => (
              <Col md={6} lg={4} key={article.id} className="mb-4">
                <Card className="h-100 shadow-sm">
                  <Card.Body>
                    <div className="d-flex justify-content-between align-items-start mb-2">
                      <Badge bg="secondary">{article.categoryName}</Badge>
                      <small className="text-muted">
                        <i className="fas fa-eye me-1"></i>
                        {article.viewCount}
                      </small>
                    </div>
                    <Card.Title>
                      <Link 
                        to={`/article/${article.id}`} 
                        className="text-decoration-none text-dark"
                      >
                        {article.title}
                      </Link>
                    </Card.Title>
                    <Card.Text className="text-muted">
                      {article.summary}
                    </Card.Text>
                  </Card.Body>
                  <Card.Footer className="bg-transparent">
                    <small className="text-muted">
                      <i className="fas fa-calendar me-1"></i>
                      {formatDate(article.publishedAt)}
                    </small>
                    <br />
                    <small className="text-muted">
                      <i className="fas fa-user me-1"></i>
                      {article.authorName}
                    </small>
                  </Card.Footer>
                </Card>
              </Col>
            ))}
          </Row>

          {totalPages > 1 && (
            <div className="d-flex justify-content-center mt-4">
              <Pagination>
                <Pagination.Prev 
                  onClick={() => setCurrentPage(currentPage - 1)}
                  disabled={currentPage === 0}
                />
                {[...Array(totalPages)].map((_, index) => (
                  <Pagination.Item
                    key={index}
                    active={index === currentPage}
                    onClick={() => setCurrentPage(index)}
                  >
                    {index + 1}
                  </Pagination.Item>
                ))}
                <Pagination.Next 
                  onClick={() => setCurrentPage(currentPage + 1)}
                  disabled={currentPage === totalPages - 1}
                />
              </Pagination>
            </div>
          )}
        </>
      )}
    </Container>
  );
}

export default CategoryList;