import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Form, Button, Card, Alert, Container } from 'react-bootstrap';
import { login } from '../services/api';
import { saveAuthData } from '../services/auth';
import { toast } from 'react-toastify';

function Login({ setUser }) {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await login(formData);
      const authData = response.data;
      
      saveAuthData(authData);
      setUser({ token: authData.token, role: authData.role });
      
      toast.success('Connexion réussie !');
      
      // Redirection selon le rôle
      if (authData.role === 'ADMIN') {
        navigate('/admin');
      } else if (authData.role === 'EDITOR') {
        navigate('/editor');
      } else {
        navigate('/');
      }
    } catch (err) {
      setError('Nom d\'utilisateur ou mot de passe incorrect');
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container className="login-container">
      <Card>
        <Card.Body>
          <h2 className="text-center mb-4">Connexion</h2>
          
          {error && <Alert variant="danger">{error}</Alert>}
          
          <Form onSubmit={handleSubmit}>
            <Form.Group className="mb-3">
              <Form.Label>Nom d'utilisateur</Form.Label>
              <Form.Control
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                required
                placeholder="Entrez votre nom d'utilisateur"
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Mot de passe</Form.Label>
              <Form.Control
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                placeholder="Entrez votre mot de passe"
              />
            </Form.Group>

            <Button
              variant="primary"
              type="submit"
              className="w-100"
              disabled={loading}
            >
              {loading ? 'Connexion...' : 'Se connecter'}
            </Button>
          </Form>
          
          <div className="mt-3 text-center">
            <small className="text-muted">
              Utilisateurs de test:<br/>
              Admin: admin / admin123<br/>
              Éditeur: editor / editor123
            </small>
          </div>
        </Card.Body>
      </Card>
    </Container>
  );
}

export default Login;