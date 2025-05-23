// src/components/layout/AppLayout.tsx (SUBSTITUIR ARQUIVO ATUAL)
import React from 'react';
import { Outlet } from 'react-router-dom';
import Header from './Header';
import Sidebar from './Sidebar';
import { MenuItem, Notification } from '../../types';

const AppLayout: React.FC = () => {
  const [collapsed, setCollapsed] = React.useState(false);
  const [notifications, setNotifications] = React.useState<Notification[]>([]);

  // Menu items vazios - o Sidebar agora gerencia internamente
  const menuItems: MenuItem[] = [];

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
        menuItems={menuItems} // Mantido para compatibilidade
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