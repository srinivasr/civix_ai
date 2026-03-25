/* eslint-disable react-refresh/only-export-components */
import React, { createContext, useContext, useState, useEffect } from 'react';

const API_BASE = 'http://localhost:8000/api/v1/auth';
const AuthContext = createContext();

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Hydrate user from stored JWT on mount
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      setLoading(false);
      return;
    }
    fetch(`${API_BASE}/me`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => {
        if (!res.ok) throw new Error('Token expired');
        return res.json();
      })
      .then((user) => {
        setCurrentUser({
          id: user.id,
          email: user.email,
          displayName: user.role,
          role: user.role,
        });
      })
      .catch(() => {
        localStorage.removeItem('token');
      })
      .finally(() => setLoading(false));
  }, []);

  async function signup(email, password, role, metadata) {
    const res = await fetch(`${API_BASE}/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email,
        password,
        role,
        display_name: metadata?.name || metadata?.department || role,
      }),
    });

    const data = await res.json();

    if (!res.ok) {
      const err = new Error(data.detail || 'Registration failed');
      err.code = data.detail; // e.g. "email-already-in-use"
      throw err;
    }

    localStorage.setItem('token', data.access_token);
    const user = {
      id: data.user.id,
      email: data.user.email,
      displayName: data.user.role,
      role: data.user.role,
    };
    setCurrentUser(user);
    return { user };
  }

  async function login(email, password) {
    const res = await fetch(`${API_BASE}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    const data = await res.json();

    if (!res.ok) {
      const err = new Error(data.detail || 'Login failed');
      err.code = data.detail; // e.g. "invalid-credentials"
      throw err;
    }

    localStorage.setItem('token', data.access_token);
    const user = {
      id: data.user.id,
      email: data.user.email,
      displayName: data.user.role,
      role: data.user.role,
    };
    setCurrentUser(user);
    return { user };
  }

  function logout() {
    localStorage.removeItem('token');
    setCurrentUser(null);
    return Promise.resolve();
  }

  const value = {
    currentUser,
    login,
    signup,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
}
