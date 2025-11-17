import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { toast } from 'react-toastify';
import { register } from '../services/authService';
import './RegisterPage.css';

const RegisterPage: React.FC = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleGoogleRegister = () => {
    // Redirect to Google OAuth endpoint (same as login)
    window.location.href = 'http://localhost:8000/auth/google/login';
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!name || !email || !password || !confirmPassword) {
      toast.error('Por favor, preencha todos os campos');
      return;
    }

    if (password !== confirmPassword) {
      toast.error('As senhas n�o coincidem');
      return;
    }

    if (password.length < 6) {
      toast.error('A senha deve ter no m�nimo 6 caracteres');
      return;
    }

    setLoading(true);
    try {
      await register({ name, email, password });
      toast.success('Conta criada com sucesso! Fa�a login para continuar.');
      navigate('/login');
    } catch (error: any) {
      console.error('Register error:', error);
      toast.error(error.response?.data?.detail || 'Erro ao criar conta');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="register-page">
      <div className="register-container">
        <div className="register-header">
          <h1>LangNet</h1>
          <p>Sistema de Gerenciamento de Agentes Multi-Agente</p>
        </div>

        <div className="register-card">
          <h2>Criar Conta</h2>

          {/* Google Register Button */}
          <button
            type="button"
            className="btn-google"
            onClick={handleGoogleRegister}
            disabled={loading}
          >
            <svg className="google-icon" viewBox="0 0 24 24" width="18" height="18">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Continuar com Google
          </button>

          {/* Divider */}
          <div className="register-divider">
            <span>ou</span>
          </div>

          {/* Email/Password Registration Form */}
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="name">Nome Completo</label>
              <input
                type="text"
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Seu nome completo"
                disabled={loading}
                autoComplete="name"
              />
            </div>

            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="seu@email.com"
                disabled={loading}
                autoComplete="email"
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Senha</label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="M�nimo 6 caracteres"
                disabled={loading}
                autoComplete="new-password"
              />
            </div>

            <div className="form-group">
              <label htmlFor="confirmPassword">Confirmar Senha</label>
              <input
                type="password"
                id="confirmPassword"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Digite a senha novamente"
                disabled={loading}
                autoComplete="new-password"
              />
            </div>

            <button
              type="submit"
              className="btn-register"
              disabled={loading}
            >
              {loading ? 'Criando conta...' : 'Criar Conta'}
            </button>
          </form>

          <div className="register-footer">
            <p>
              J� tem uma conta? <Link to="/login">Fa�a login</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
