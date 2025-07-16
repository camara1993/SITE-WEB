import React, { useState, useEffect } from 'react';
import { Container, Tabs, Tab, Table, Button, Modal, Form, Badge } from 'react-bootstrap';
import { toast } from 'react-toastify';
import { 
  createArticle, 
  updateArticle, 
  deleteArticle, 
  getCategories,
  createCategory,
  updateCategory,
  deleteCategory,
  getAllArticlesRest
} from '../services/api';
import { getUserId } from '../services/auth';

function EditorPanel() {
  const [activeTab, setActiveTab] = useState('articles');
  const [articles, setArticles] = useState([]);
  const [categories, setCategories] = useState([]);
  const [showArticleModal, setShowArticleModal] = useState(false);
  const [showCategoryModal, setShowCategoryModal] = useState(false);
  const [editingArticle, setEditingArticle] = useState(null);
  const [editingCategory, setEditingCategory] = useState(null);
  const [loading, setLoading] = useState(false);

  const [articleForm, setArticleForm] = useState({
    title: '',
    summary: '',
    content: '',
    category: { id: null },
    published: false
  });

  const [categoryForm, setCategoryForm] = useState({
    name: '',
    description: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [articlesRes, categoriesRes] = await Promise.all([
        getAllArticlesRest(),
        getCategories()
      ]);
      setArticles(articlesRes.data);
      setCategories(categoriesRes.data);
    } catch (error) {
      toast.error('Erreur lors du chargement des données');
    } finally {
      setLoading(false);
    }
  };

  // Gestion des articles
  const handleArticleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingArticle) {
        await updateArticle(editingArticle.id, articleForm);
        toast.success('Article mis à jour avec succès');
      } else {
        await createArticle(articleForm);
        toast.success('Article créé avec succès');
      }
      setShowArticleModal(false);
      resetArticleForm();
      loadData();
    } catch (error) {
      toast.error('Erreur lors de l\'enregistrement de l\'article');
    }
  };

  const handleEditArticle = (article) => {
    setEditingArticle(article);
    setArticleForm({
      title: article.title,
      summary: article.summary,
      content: article.content,
      category: { id: article.categoryId },
      published: article.published
    });
    setShowArticleModal(true);
  };

  const handleDeleteArticle = async (id) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer cet article ?')) {
      try {
        await deleteArticle(id);
        toast.success('Article supprimé avec succès');
        loadData();
      } catch (error) {
        toast.error('Erreur lors de la suppression');
      }
    }
  };

  const resetArticleForm = () => {
    setArticleForm({
      title: '',
      summary: '',
      content: '',
      category: { id: null },
      published: false
    });
    setEditingArticle(null);
  };

  // Gestion des catégories
  const handleCategorySubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingCategory) {
        await updateCategory(editingCategory.id, categoryForm);
        toast.success('Catégorie mise à jour avec succès');
      } else {
        await createCategory(categoryForm);
        toast.success('Catégorie créée avec succès');
      }
      setShowCategoryModal(false);
      resetCategoryForm();
      loadData();
    } catch (error) {
      toast.error('Erreur lors de l\'enregistrement de la catégorie');
    }
  };

  const handleEditCategory = (category) => {
    setEditingCategory(category);
    setCategoryForm({
      name: category.name,
      description: category.description || ''
    });
    setShowCategoryModal(true);
  };

  const handleDeleteCategory = async (id) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer cette catégorie ?')) {
      try {
        await deleteCategory(id);
        toast.success('Catégorie supprimée avec succès');
        loadData();
      } catch (error) {
        toast.error('Erreur lors de la suppression');
      }
    }
  };

  const resetCategoryForm = () => {
    setCategoryForm({
      name: '',
      description: ''
    });
    setEditingCategory(null);
  };

  return (
    <Container className="mt-4">
      <h1 className="mb-4">Panneau Éditeur</h1>

      <Tabs activeKey={activeTab} onSelect={setActiveTab} className="mb-4">
        <Tab eventKey="articles" title="Articles">
          <div className="editor-panel">
            <div className="d-flex justify-content-between mb-3">
              <h3>Gestion des Articles</h3>
              <Button 
                variant="primary" 
                onClick={() => setShowArticleModal(true)}
              >
                <i className="fas fa-plus me-2"></i>
                Nouvel Article
              </Button>
            </div>

            <Table striped bordered hover responsive>
              <thead>
                <tr>
                  <th>Titre</th>
                  <th>Catégorie</th>
                  <th>Auteur</th>
                  <th>Statut</th>
                  <th>Vues</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {articles.map(article => (
                  <tr key={article.id}>
                    <td>{article.title}</td>
                    <td>{article.categoryName}</td>
                    <td>{article.authorName}</td>
                    <td>
                      <Badge bg={article.published ? 'success' : 'warning'}>
                        {article.published ? 'Publié' : 'Brouillon'}
                      </Badge>
                    </td>
                    <td>{article.viewCount}</td>
                    <td className="table-actions">
                      <Button 
                        size="sm" 
                        variant="info" 
                        onClick={() => handleEditArticle(article)}
                      >
                        <i className="fas fa-edit"></i>
                      </Button>
                      <Button 
                        size="sm" 
                        variant="danger" 
                        onClick={() => handleDeleteArticle(article.id)}
                      >
                        <i className="fas fa-trash"></i>
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </div>
        </Tab>

        <Tab eventKey="categories" title="Catégories">
          <div className="editor-panel">
            <div className="d-flex justify-content-between mb-3">
              <h3>Gestion des Catégories</h3>
              <Button 
                variant="primary" 
                onClick={() => setShowCategoryModal(true)}
              >
                <i className="fas fa-plus me-2"></i>
                Nouvelle Catégorie
              </Button>
            </div>

            <Table striped bordered hover responsive>
              <thead>
                <tr>
                  <th>Nom</th>
                  <th>Description</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {categories.map(category => (
                  <tr key={category.id}>
                    <td>{category.name}</td>
                    <td>{category.description}</td>
                    <td className="table-actions">
                      <Button 
                        size="sm" 
                        variant="info" 
                        onClick={() => handleEditCategory(category)}
                      >
                        <i className="fas fa-edit"></i>
                      </Button>
                      <Button 
                        size="sm" 
                        variant="danger" 
                        onClick={() => handleDeleteCategory(category.id)}
                      >
                        <i className="fas fa-trash"></i>
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </div>
        </Tab>
      </Tabs>

      {/* Modal Article */}
      <Modal 
        show={showArticleModal} 
        onHide={() => {
          setShowArticleModal(false);
          resetArticleForm();
        }}
        size="lg"
      >
        <Modal.Header closeButton>
          <Modal.Title>
            {editingArticle ? 'Modifier l\'article' : 'Nouvel article'}
          </Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleArticleSubmit}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label>Titre</Form.Label>
              <Form.Control
                type="text"
                value={articleForm.title}
                onChange={(e) => setArticleForm({...articleForm, title: e.target.value})}
                required
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Résumé</Form.Label>
              <Form.Control
                as="textarea"
                rows={2}
                value={articleForm.summary}
                onChange={(e) => setArticleForm({...articleForm, summary: e.target.value})}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Contenu</Form.Label>
              <Form.Control
                as="textarea"
                rows={6}
                value={articleForm.content}
                onChange={(e) => setArticleForm({...articleForm, content: e.target.value})}
                required
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Catégorie</Form.Label>
              <Form.Select
                value={articleForm.category.id || ''}
                onChange={(e) => setArticleForm({
                  ...articleForm, 
                  category: { id: parseInt(e.target.value) }
                })}
                required
              >
                <option value="">Sélectionner une catégorie</option>
                {categories.map(cat => (
                  <option key={cat.id} value={cat.id}>{cat.name}</option>
                ))}
              </Form.Select>
            </Form.Group>

            <Form.Check
              type="checkbox"
              label="Publier l'article"
              checked={articleForm.published}
              onChange={(e) => setArticleForm({...articleForm, published: e.target.checked})}
            />
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => {
              setShowArticleModal(false);
              resetArticleForm();
            }}>
              Annuler
            </Button>
            <Button variant="primary" type="submit">
              {editingArticle ? 'Mettre à jour' : 'Créer'}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>

      {/* Modal Catégorie */}
      <Modal 
        show={showCategoryModal} 
        onHide={() => {
          setShowCategoryModal(false);
          resetCategoryForm();
        }}
      >
        <Modal.Header closeButton>
          <Modal.Title>
            {editingCategory ? 'Modifier la catégorie' : 'Nouvelle catégorie'}
          </Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleCategorySubmit}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label>Nom</Form.Label>
              <Form.Control
                type="text"
                value={categoryForm.name}
                onChange={(e) => setCategoryForm({...categoryForm, name: e.target.value})}
                required
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Description</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={categoryForm.description}
                onChange={(e) => setCategoryForm({...categoryForm, description: e.target.value})}
              />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => {
              setShowCategoryModal(false);
              resetCategoryForm();
            }}>
              Annuler
            </Button>
            <Button variant="primary" type="submit">
              {editingCategory ? 'Mettre à jour' : 'Créer'}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </Container>
  );
}

export default EditorPanel;