import React from 'react';
import { Link } from 'react-router-dom';
import { MenuItem } from '../../types';

interface SidebarProps {
  menuItems: MenuItem[];
  collapsed: boolean;
  onToggleCollapse: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ menuItems, collapsed, onToggleCollapse }) => {
  return (
    <div className={`sidebar ${collapsed ? 'sidebar-collapsed' : ''}`}>
      <div className="sidebar-header">
        <h2 className="logo">LangNet</h2>
        <button className="collapse-btn" onClick={onToggleCollapse}>
          {collapsed ? '→' : '←'}
        </button>
      </div>
      <nav className="sidebar-nav">
        <ul>
          {menuItems.map((item) => (
            <li key={item.id} className="nav-item">
              <Link to={item.path} className="nav-link">
                <span className="nav-icon">{item.icon}</span>
                {!collapsed && <span className="nav-label">{item.label}</span>}
              </Link>
              {!collapsed && item.children && (
                <ul className="nav-children">
                  {item.children.map((child) => (
                    <li key={child.id} className="nav-child-item">
                      <Link to={child.path} className="nav-child-link">
                        <span className="nav-child-icon">{child.icon}</span>
                        <span className="nav-child-label">{child.label}</span>
                      </Link>
                    </li>
                  ))}
                </ul>
              )}
            </li>
          ))}
        </ul>
      </nav>
    </div>
  );
};

export default Sidebar;
