import React from 'react';
import { Outlet } from 'react-router-dom';
import Header from './Header';
import Sidebar from './Sidebar';
import { MenuItem, Notification } from '../../types';

const AppLayout: React.FC = () => {
  const [collapsed, setCollapsed] = React.useState(false);
  const [notifications, setNotifications] = React.useState<Notification[]>([]);

  // Menu items para a sidebar
  const menuItems: MenuItem[] = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: '📊',
      path: '/'
    },
    {
      id: 'projects',
      label: 'Projetos',
      icon: '📁',
      path: '/projects'
    },
    {
      id: 'settings',
      label: 'Configurações',
      icon: '⚙️',
      path: '/settings'
    },
    {
      id: 'help',
      label: 'Ajuda',
      icon: '❓',
      path: '/help'
    }
  ];

  const handleToggleCollapse = () => {
    setCollapsed(!collapsed);
  };

  const handleNotificationClick = (id: string) => {
    setNotifications(
      notifications.map(notification =>
        notification.id === id ? { ...notification, read: true } : notification
      )
    );
  };

  const handleProfileClick = () => {
    console.log('Profile clicked');
  };

  const handleSearchSubmit = (query: string) => {
    console.log('Search query:', query);
  };

  return (
    <div className="app-container">
      <Sidebar 
        menuItems={menuItems} 
        collapsed={collapsed} 
        onToggleCollapse={handleToggleCollapse} 
      />
      <div className="main-content">
        <Header 
          title="LangNet"
          notifications={notifications}
          onNotificationClick={handleNotificationClick}
          onProfileClick={handleProfileClick}
          onSearchSubmit={handleSearchSubmit}
        />
        <main className="content-area">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default AppLayout;
