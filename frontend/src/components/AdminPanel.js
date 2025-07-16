import React, { useState, useEffect } from 'react';
import { Container, Tabs, Tab, Table, Button, Modal, Form, Badge } from 'react-bootstrap';
import { toast } from 'react-toastify';
import { 
  getUsers, 
  createUser, 
  updateUser, 
  deleteUser,
  getTokens,
  createToken,
  revokeToken
} from '../services/api';
import EditorPanel from './EditorPanel';

function AdminPanel() {
  const [activeTab, setActiveTab] = useState('users');
  const [users, setUsers] = useState([]);
  const [tokens, setTokens] = useState([]);
  const [showUserModal, setShowUserModal] = useState(false);
  const [showTokenModal, setShowTokenModal] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [loading, setLoading] = useState(false);

  const [userForm, setUserForm] = useState({
    username: '',
    email: '',
    password: '',
    firstName: '',
    lastName: '',
    role: 'VISITOR',
    active: true
  });

  const [tokenForm, setTokenForm] = useState({
    description: '',
    expiresInDays: 30
  });

  useEffect(() => {
    loadUsers();
    loadTokens();
  }, []);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const response = await getUsers();
      setUsers(response.data);
    } catch (error) {
      toast.error('Erreur lors du chargement des utilisateurs');
    } finally {
      setLoading(false);
    }
  };

  const loadTokens = async () => {
    try {
      const response = await getTokens();
      setTokens(response.data);
    } catch (error) {
      toast.error('Erreur lors du chargement des tokens');
    }
  };

  // Gestion des utilisateurs
  const handleUserSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingUser) {
        await updateUser(editingUser.id, userForm);
        toast.success('Utilisateur mis à jour avec succès');
      } else {
        await createUser(userForm);
        toast.success('Utilisateur créé avec succès');
      }
      setShowUserModal(false);
      resetUserForm();
      loadUsers();
    } catch (error) {
      toast.error('Erreur lors de l\'enregistrement de l\'utilisateur');
    }
  };

  const handleEditUser = (user) => {
    setEditingUser(user);
    setUserForm({
      username: user.username,
      email: user.email,
      password: '',
      firstName: user.firstName || '',
      lastName: user.lastName || '',
      role: user.role,
      active: user.active
    });
    setShowUserModal(true);
  };

  const handleDeleteUser = async (id) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer cet utilisateur ?')) {
      try {
        await deleteUser(id);
        toast.success('Utilisateur supprimé avec succès');
        loadUsers();
      } catch (error) {
        toast.error('Erreur lors de la suppression');
      }
    }
  };

  const resetUserForm = () => {
    setUserForm({
      username: '',
      email: '',
      password: '',
      firstName: '',
      lastName: '',
      role: 'VISITOR',
      active: true
    });
    setEditingUser(null);
  };

  // Gestion des tokens
  const handleTokenSubmit = async (e) => {
    e.preventDefault();
    try {
      await createToken(tokenForm);
      toast.success('Token créé avec succès');
      setShowTokenModal(false);
      resetTokenForm();
      loadTokens();
    } catch (error) {
      toast.error('Erreur lors de la création du token');
    }
  };

  const handleRevokeToken = async (token) => {
    if (window.confirm('Êtes-vous sûr de vouloir révoquer ce token ?')) {
      try {
        await revokeToken(token);
        toast.success('Token révoqué avec succès');
        loadTokens();
      } catch (error) {
        toast.error('Erreur lors de la révocation du token');
      }
    }
  };

  const resetTokenForm = () => {
    setTokenForm({
      description: '',
      expiresInDays: 30
    });
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <Container className="mt-4">
      <h1 className="mb-4">Panneau Administration</h1>

      <Tabs activeKey={activeTab} onSelect={setActiveTab} className="mb-4">
        <Tab eventKey="users" title="Utilisateurs">
          <div className="admin-panel">
            <div className="d-flex justify-content-between mb-3">
              <h3>Gestion des Utilisateurs</h3>
              <Button 
                variant="primary" 
                onClick={() => setShowUserModal(true)}
              >
                <i className="fas fa-plus me-2"></i>
                Nouvel Utilisateur
              </Button>
            </div>

            <Table striped bordered hover responsive>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Nom d'utilisateur</th>
                  <th>Email</th>
                  <th>Nom complet</th>
                  <th>Rôle</th>
                  <th>Statut</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map(user => (
                  <tr key={user.id}>
                    <td>{user.id}</td>
                    <td>{user.username}</td>
                    <td>{user.email}</td>
                    <td>{user.firstName} {user.lastName}</td>
                    <td>
                      <Badge bg={
                        user.role === 'ADMIN' ? 'danger' : 
                        user.role === 'EDITOR' ? 'warning' : 
                        'secondary'
                      }>
                        {user.role}
                      </Badge>
                    </td>
                    <td>
                      <Badge bg={user.active ? 'success' : 'danger'}>
                        {user.active ? 'Actif' : 'Inactif'}
                      </Badge>
                    </td>
                    <td className="table-actions">
                      <Button 
                        size="sm" 
                        variant="info" 
                        onClick={() => handleEditUser(user)}
                      >
                        <i className="fas fa-edit"></i>
                      </Button>
                      <Button 
                        size="sm" 
                        variant="danger" 
                        onClick={() => handleDeleteUser(user.id)}
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

        <Tab eventKey="tokens" title="Tokens API">
          <div className="admin-panel">
            <div className="d-flex justify-content-between mb-3">
              <h3>Gestion des Tokens d'Authentification</h3>
              <Button 
                variant="primary" 
                onClick={() => setShowTokenModal(true)}
              >
                <i className="fas fa-plus me-2"></i>
                Nouveau Token
              </Button>
            </div>

            <Table striped bordered hover responsive>
              <thead>
                <tr>
                  <th>Token</th>
                  <th>Description</th>
                  <th>Créé par</th>
                  <th>Date de création</th>
                  <th>Expiration</th>
                  <th>Dernière utilisation</th>
                  <th>Statut</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {tokens.map(token => (
                  <tr key={token.id}>
                    <td>
                      <code>{token.token.substring(0, 8)}...</code>
                    </td>
                    <td>{token.description}</td>
                    <td>{token.createdBy?.username}</td>
                    <td>{formatDate(token.createdAt)}</td>
                    <td>{formatDate(token.expiresAt)}</td>
                    <td>{formatDate(token.lastUsedAt)}</td>
                    <td>
                      <Badge bg={token.active ? 'success' : 'danger'}>
                        {token.active ? 'Actif' : 'Révoqué'}
                      </Badge>
                    </td>
                    <td className="table-actions">
                      {token.active && (
                        <Button 
                          size="sm" 
                          variant="danger" 
                          onClick={() => handleRevokeToken(token.token)}
                        >
                          Révoquer
                        </Button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </div>
        </Tab>

        <Tab eventKey="editor" title="Éditeur">
          <EditorPanel />
        </Tab>
      </Tabs>

      {/* Modal Utilisateur */}
      <Modal 
        show={showUserModal} 
        onHide={() => {
          setShowUserModal(false);
          resetUserForm();
        }}
      >
        <Modal.Header closeButton>
          <Modal.Title>
            {editingUser ? 'Modifier l\'utilisateur' : 'Nouvel utilisateur'}
          </Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleUserSubmit}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label>Nom d'utilisateur</Form.Label>
              <Form.Control
                type="text"
                value={userForm.username}
                onChange={(e) => setUserForm({...userForm, username: e.target.value})}
                required
                disabled={editingUser}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Email</Form.Label>
              <Form.Control
                type="email"
                value={userForm.email}
                onChange={(e) => setUserForm({...userForm, email: e.target.value})}
                required
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Mot de passe {editingUser && '(laisser vide pour ne pas changer)'}</Form.Label>
              <Form.Control
                type="password"
                value={userForm.password}
                onChange={(e) => setUserForm({...userForm, password: e.target.value})}
                required={!editingUser}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Prénom</Form.Label>
              <Form.Control
                type="text"
                value={userForm.firstName}
                onChange={(e) => setUserForm({...userForm, firstName: e.target.value})}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Nom</Form.Label>
              <Form.Control
                type="text"
                value={userForm.lastName}
                onChange={(e) => setUserForm({...userForm, lastName: e.target.value})}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Rôle</Form.Label>
              <Form.Select
                value={userForm.role}
                onChange={(e) => setUserForm({...userForm, role: e.target.value})}
              >
                <option value="VISITOR">Visiteur</option>
                <option value="EDITOR">Éditeur</option>
                <option value="ADMIN">Administrateur</option>
              </Form.Select>
            </Form.Group>

            <Form.Check
              type="checkbox"
              label="Compte actif"
              checked={userForm.active}
              onChange={(e) => setUserForm({...userForm, active: e.target.checked})}
            />
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => {
              setShowUserModal(false);
              resetUserForm();
            }}>
              Annuler
            </Button>
            <Button variant="primary" type="submit">
              {editingUser ? 'Mettre à jour' : 'Créer'}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>

      {/* Modal Token */}
      <Modal 
        show={showTokenModal} 
        onHide={() => {
          setShowTokenModal(false);
          resetTokenForm();
        }}
      >
        <Modal.Header closeButton>
          <Modal.Title>Nouveau Token d'Authentification</Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleTokenSubmit}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label>Description</Form.Label>
              <Form.Control
                type="text"
                value={tokenForm.description}
                onChange={(e) => setTokenForm({...tokenForm, description: e.target.value})}
                required
                placeholder="Ex: Token pour application mobile"
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Durée de validité (jours)</Form.Label>
              <Form.Control
                type="number"
                value={tokenForm.expiresInDays}
                onChange={(e) => setTokenForm({...tokenForm, expiresInDays: parseInt(e.target.value)})}
                min="1"
                max="365"
              />
              <Form.Text className="text-muted">
                Laisser vide pour un token sans expiration
              </Form.Text>
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => {
              setShowTokenModal(false);
              resetTokenForm();
            }}>
              Annuler
            </Button>
            <Button variant="primary" type="submit">
              Créer le token
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </Container>
  );
}

export default AdminPanel;