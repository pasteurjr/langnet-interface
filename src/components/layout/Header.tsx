import React from 'react';
import { Notification } from '../../types';

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
        <button className="profile-btn" onClick={onProfileClick}>
          👤
        </button>
      </div>
    </header>
  );
};

export default Header;
