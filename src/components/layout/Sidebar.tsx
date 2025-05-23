// src/components/layout/Sidebar.tsx (SUBSTITUIR ARQUIVO ATUAL)
import React from 'react';
import { Link } from 'react-router-dom';
import { MenuItem } from '../../types';
import { useNavigation } from '../../contexts/NavigationContext';
import './Sidebar.css';

interface SidebarProps {
  menuItems: MenuItem[]; // Mantido para compatibilidade, mas será sobrescrito
  collapsed: boolean;
  onToggleCollapse: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ collapsed, onToggleCollapse }) => {
  const { menuItems, projectContext, exitProjectContext } = useNavigation();

  return (
    <div className={`sidebar ${collapsed ? 'sidebar-collapsed' : ''}`}>
      <div className="sidebar-header">
        <h2 className="logo">
          {projectContext.isInProject && !collapsed ? projectContext.projectName : 'LangNet'}
        </h2>
        <button className="collapse-btn" onClick={onToggleCollapse}>
          {collapsed ? '→' : '←'}
        </button>
      </div>

      {/* Botão de Voltar - apenas quando em contexto de projeto */}
      {projectContext.isInProject && (
        <div className="back-section">
          <button 
            className="back-button"
            onClick={exitProjectContext}
            title="Voltar ao Dashboard"
          >
            <span className="back-icon">←</span>
            {!collapsed && <span>Voltar ao Dashboard</span>}
          </button>
        </div>
      )}

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

      {/* Status do Projeto - apenas quando em contexto de projeto */}
      {projectContext.isInProject && !collapsed && (
        <div className="project-status">
          <div className="status-item">
            <span className="status-label">ID do Projeto:</span>
            <span className="status-value">{projectContext.projectId}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default Sidebar;
