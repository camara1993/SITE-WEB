import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import '@fortawesome/fontawesome-free/css/all.min.css';

import Header from './components/Header';
import ArticleList from './components/ArticleList';
import ArticleDetail from './components/ArticleDetail';
import CategoryList from './components/CategoryList';
import Login from './components/Login';
import AdminPanel from './components/AdminPanel';
import EditorPanel from './components/EditorPanel';
import { getAuthToken, getUserRole } from './services/auth';

function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const token = getAuthToken();
    if (token) {
      const role = getUserRole();
      setUser({ token, role });
    }
  }, []);

  const PrivateRoute = ({ children, requiredRole }) => {
    if (!user) {
      return <Navigate to="/login" />;
    }
    
    if (requiredRole && user.role !== requiredRole && user.role !== 'ADMIN') {
      return <Navigate to="/" />;
    }
    
    return children;
  };

  return (
    <Router>
      <div className="App">
        <Header user={user} setUser={setUser} />
        <main className="container mt-4">
          <Routes>
            <Route path="/" element={<ArticleList />} />
            <Route path="/article/:id" element={<ArticleDetail />} />
            <Route path="/category/:id" element={<CategoryList />} />
            <Route path="/login" element={<Login setUser={setUser} />} />
            <Route 
              path="/editor" 
              element={
                <PrivateRoute requiredRole="EDITOR">
                  <EditorPanel />
                </PrivateRoute>
              } 
            />
            <Route 
              path="/admin" 
              element={
                <PrivateRoute requiredRole="ADMIN">
                  <AdminPanel />
                </PrivateRoute>
              } 
            />
          </Routes>
        </main>
        <ToastContainer position="bottom-right" />
      </div>
    </Router>
  );
}

export default App;