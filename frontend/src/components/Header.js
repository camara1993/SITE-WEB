import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Navbar, Nav, Container, NavDropdown } from 'react-bootstrap';
import { getCategories } from '../services/api';
import { logout } from '../services/auth';

function Header({ user, setUser }) {
  const [categories, setCategories] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    loadCategories();
  }, []);

  const loadCategories = async () => {
    try {
      const response = await getCategories();
      setCategories(response.data);
    } catch (error) {
      console.error('Error loading categories:', error);
    }
  };

  const handleLogout = () => {
    logout();
    setUser(null);
    navigate('/');
  };

  return (
    <Navbar bg="dark" variant="dark" expand="lg">
      <Container>
        <Navbar.Brand as={Link} to="/">
          <i className="fas fa-newspaper me-2"></i>
          News Platform
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
            <Nav.Link as={Link} to="/">Accueil</Nav.Link>
            <NavDropdown title="Catégories" id="categories-dropdown">
              {categories.map(category => (
                <NavDropdown.Item 
                  key={category.id} 
                  as={Link} 
                  to={`/category/${category.id}`}
                >
                  {category.name}
                </NavDropdown.Item>
              ))}
            </NavDropdown>
          </Nav>
          <Nav>
            {user ? (
              <>
                {(user.role === 'EDITOR' || user.role === 'ADMIN') && (
                  <Nav.Link as={Link} to="/editor">
                    <i className="fas fa-edit me-1"></i> Éditeur
                  </Nav.Link>
                )}
                {user.role === 'ADMIN' && (
                  <Nav.Link as={Link} to="/admin">
                    <i className="fas fa-cog me-1"></i> Administration
                  </Nav.Link>
                )}
                <Nav.Link onClick={handleLogout}>
                  <i className="fas fa-sign-out-alt me-1"></i> Déconnexion
                </Nav.Link>
              </>
            ) : (
              <Nav.Link as={Link} to="/login">
                <i className="fas fa-sign-in-alt me-1"></i> Connexion
              </Nav.Link>
            )}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
}

export default Header;