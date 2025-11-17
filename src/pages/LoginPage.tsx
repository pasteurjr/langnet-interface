import React, { useState, useEffect } from 'react';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import { toast } from 'react-toastify';
import { login } from '../services/authService';
import './LoginPage.css';

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email || !password) {
      toast.error('Por favor, preencha todos os campos');
      return;
    }

    setLoading(true);
    try {
      const response = await login({ email, password });
      toast.success(`Bem-vindo, ${response.user.name}!`);
      navigate('/');
    } catch (error: any) {
      console.error('Login error:', error);
      toast.error(error.response?.data?.detail || 'Erro ao fazer login');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = () => {
    // Redirect to Google OAuth endpoint
    window.location.href = 'http://localhost:8000/auth/google/login';
  };

  // Handle OAuth callback (token in URL)
  useEffect(() => {
    const token = searchParams.get('token');
    const name = searchParams.get('name');
    const error = searchParams.get('error');

    if (error) {
      toast.error('Erro ao autenticar com Google');
      return;
    }

    if (token) {
      // Store token using standard key 'accessToken'
      localStorage.setItem('accessToken', token);

      // Show success message
      toast.success(`Bem-vindo, ${name || 'Usuário'}!`);

      // Redirect to home
      navigate('/');
    }
  }, [searchParams, navigate]);

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-header">
          <h1>LangNet</h1>
          <p>Sistema de Gerenciamento de Agentes Multi-Agente</p>
        </div>

        <div className="login-card">
          <h2>Entrar na sua conta</h2>

          {/* Google Login Button */}
          <button
            type="button"
            className="btn-google"
            onClick={handleGoogleLogin}
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
          <div className="login-divider">
            <span>ou</span>
          </div>

          {/* Email/Password Login Form */}
          <form onSubmit={handleSubmit}>
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
                placeholder="Senha"
                disabled={loading}
                autoComplete="current-password"
              />
            </div>

            <button
              type="submit"
              className="btn-login"
              disabled={loading}
            >
              {loading ? 'Entrando...' : 'Entrar'}
            </button>
          </form>

          <div className="login-footer">
            <p>
              Não tem uma conta? <Link to="/register" className="register-link">Registre-se aqui</Link>
            </p>
          </div>
        </div>

        <div className="login-info">
          <p className="test-credentials">
            <strong>Credenciais de teste:</strong><br />
            Email: teste@teste.com<br />
            Senha: teste
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
