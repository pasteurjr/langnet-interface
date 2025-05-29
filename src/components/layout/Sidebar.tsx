// src/components/layout/Sidebar.tsx (SUBSTITUIR ARQUIVO ATUAL)
import React, { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { MenuItem } from "../../types";
import { useNavigation } from "../../contexts/NavigationContext";
import "./Sidebar.css";

interface SidebarProps {
  menuItems: MenuItem[]; // Mantido para compatibilidade, mas será sobrescrito
  collapsed: boolean;
  onToggleCollapse: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ collapsed, onToggleCollapse }) => {
  const { menuItems, projectContext, exitProjectContext } = useNavigation();

  const location = useLocation();
  const [expandedItems, setExpandedItems] = useState<string[]>(["mcp"]); // MCP expandido por padrão
  const toggleExpanded = (itemId: string) => {
    setExpandedItems((prev) =>
      prev.includes(itemId)
        ? prev.filter((id) => id !== itemId)
        : [...prev, itemId]
    );
  };

  const isActiveRoute = (path: string) => {
    return (
      location.pathname === path || location.pathname.startsWith(path + "/")
    );
  };

  return (
    <div className={`sidebar ${collapsed ? "sidebar-collapsed" : ""}`}>
      <div className="sidebar-header">
        <h2 className="logo">
          {projectContext.isInProject && !collapsed
            ? projectContext.projectName
            : "LangNet"}
        </h2>
        <button className="collapse-btn" onClick={onToggleCollapse}>
          {collapsed ? "→" : "←"}
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
              {item.children && item.children.length > 0 ? (
                // Item com submenu
                <div className="nav-item-with-children">
                  <div
                    className={`nav-link nav-parent ${
                      isActiveRoute(item.path) ? "active" : ""
                    }`}
                    onClick={() => !collapsed && toggleExpanded(item.id)}
                  >
                    <span className="nav-icon">{item.icon}</span>
                    {!collapsed && (
                      <>
                        <span className="nav-label">{item.label}</span>
                        <span
                          className={`nav-arrow ${
                            expandedItems.includes(item.id) ? "expanded" : ""
                          }`}
                        >
                          ▼
                        </span>
                      </>
                    )}
                  </div>

                  {!collapsed && expandedItems.includes(item.id) && (
                    <ul className="nav-children">
                      {item.children.map((child) => (
                        <li key={child.id} className="nav-child-item">
                          <Link
                            to={child.path}
                            className={`nav-child-link ${
                              isActiveRoute(child.path) ? "active" : ""
                            }`}
                          >
                            <span className="nav-child-icon">{child.icon}</span>
                            <span className="nav-child-label">
                              {child.label}
                            </span>
                          </Link>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              ) : (
                // Item normal sem submenu
                <Link
                  to={item.path}
                  className={`nav-link ${
                    isActiveRoute(item.path) ? "active" : ""
                  }`}
                >
                  <span className="nav-icon">{item.icon}</span>
                  {!collapsed && (
                    <span className="nav-label">{item.label}</span>
                  )}
                </Link>
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
