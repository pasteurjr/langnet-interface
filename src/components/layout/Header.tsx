import React from 'react';
import { Notification } from '../../types';
import { getCurrentUser, logout } from '../../services/authService';

interface HeaderProps {
  title: string;
  notifications: Notification[];
  onNotificationClick: (id: string) => void;
  onProfileClick: () => void;
  onSearchSubmit: (query: string) => void;
}

const Header: React.FC<HeaderProps> = ({
  title,
  notifications,
  onNotificationClick,
  onProfileClick,
  onSearchSubmit
}) => {
  const [searchQuery, setSearchQuery] = React.useState('');
  const [showNotifications, setShowNotifications] = React.useState(false);
  const [showProfileMenu, setShowProfileMenu] = React.useState(false);
  const currentUser = getCurrentUser();

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearchSubmit(searchQuery);
  };

  const toggleNotifications = () => {
    setShowNotifications(!showNotifications);
  };

  const toggleProfileMenu = () => {
    setShowProfileMenu(!showProfileMenu);
  };

  const handleLogout = () => {
    logout();
  };

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <header className="app-header">
      <div className="header-title">
        <h1>{title}</h1>
      </div>
      <div className="header-search">
        <form onSubmit={handleSearchSubmit}>
          <input
            type="text"
            placeholder="Buscar..."
            value={searchQuery}
            onChange={handleSearchChange}
          />
          <button type="submit">🔍</button>
        </form>
      </div>
      <div className="header-actions">
        <div className="notifications-container">
          <button className="notification-btn" onClick={toggleNotifications}>
            🔔
            {unreadCount > 0 && <span className="notification-badge">{unreadCount}</span>}
          </button>
          {showNotifications && (
            <div className="notifications-dropdown">
              <h3>Notificações</h3>
              {notifications.length === 0 ? (
                <p>Nenhuma notificação</p>
              ) : (
                <ul>
                  {notifications.map(notification => (
                    <li
                      key={notification.id}
                      className={`notification-item ${!notification.read ? 'unread' : ''}`}
                      onClick={() => onNotificationClick(notification.id)}
                    >
                      <div className="notification-title">{notification.title}</div>
                      <div className="notification-message">{notification.message}</div>
                      <div className="notification-time">
                        {new Date(notification.timestamp).toLocaleTimeString()}
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </div>
        <div className="profile-container">
          <button className="profile-btn" onClick={toggleProfileMenu}>
            <span className="profile-icon">👤</span>
            {currentUser && <span className="profile-name">{currentUser.name}</span>}
          </button>
          {showProfileMenu && (
            <div className="profile-dropdown">
              {currentUser && (
                <>
                  <div className="profile-info">
                    <div className="profile-email">{currentUser.email}</div>
                    {currentUser.role && (
                      <div className="profile-role">{currentUser.role}</div>
                    )}
                  </div>
                  <div className="profile-divider"></div>
                </>
              )}
              <button className="profile-menu-item" onClick={onProfileClick}>
                Perfil
              </button>
              <button className="profile-menu-item logout" onClick={handleLogout}>
                Sair
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
