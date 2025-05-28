// src/components/settings/UserManagement.tsx
import React, { useState } from 'react';
import { 
  Users, 
  Plus, 
  Edit3, 
  Trash2, 
  Shield, 
  Mail, 
  Calendar, 
  MoreVertical, 
  Search,
  Filter,
  UserCheck,
  UserX,
  Crown
} from 'lucide-react';
import { User, UserRole } from '../../types/settings';
import './settings.css';

// Definir tipos locais que não existem no settings.ts
interface Role {
  id: string;
  name: string;
  description: string;
  permissions: string[];
}

type PermissionType = 
  | 'read_projects'
  | 'write_projects' 
  | 'delete_projects'
  | 'manage_users'
  | 'manage_system'
  | 'deploy_applications'
  | 'view_monitoring'
  | 'manage_integrations';

interface UserManagementProps {
  users: User[];
  roles: Role[];
  onUpdateUser: (userId: string, updates: Partial<User>) => void;
  onDeleteUser: (userId: string) => void;
  onCreateUser: (user: Omit<User, 'id'>) => void;
  onCreateRole: (role: Omit<Role, 'id'>) => void;
}

const UserManagement: React.FC<UserManagementProps> = ({
  users,
  roles,
  onUpdateUser,
  onDeleteUser,
  onCreateUser,
  onCreateRole
}) => {
  const [activeTab, setActiveTab] = useState<'users' | 'roles'>('users');
  const [showUserModal, setShowUserModal] = useState(false);
  const [showRoleModal, setShowRoleModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('');

  const [newUser, setNewUser] = useState({
    name: '',
    email: '',
    role: UserRole.VIEWER,
    isActive: true
  });

  const [newRole, setNewRole] = useState({
    name: '',
    description: '',
    permissions: [] as string[]
  });

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = !roleFilter || user.role === roleFilter;
    return matchesSearch && matchesRole;
  });

  const handleCreateUser = () => {
    if (newUser.name && newUser.email && newUser.role) {
      onCreateUser({
        name: newUser.name,
        email: newUser.email,
        role: newUser.role,
        isActive: newUser.isActive,
        permissions: [],
        projects: [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        lastLogin: undefined
      });
      setNewUser({
        name: '',
        email: '',
        role: UserRole.VIEWER,
        isActive: true
      });
      setShowUserModal(false);
    }
  };

  const handleCreateRole = () => {
    if (newRole.name && newRole.description) {
      onCreateRole(newRole);
      setNewRole({
        name: '',
        description: '',
        permissions: []
      });
      setShowRoleModal(false);
    }
  };

  const toggleUserStatus = (userId: string, currentStatus: boolean) => {
    onUpdateUser(userId, { isActive: !currentStatus });
  };

  const getStatusIcon = (isActive: boolean) => {
    return isActive ? <UserCheck className="w-4 h-4" /> : <UserX className="w-4 h-4" />;
  };

  const getRoleIcon = (role: UserRole) => {
    switch (role) {
      case UserRole.ADMIN: return <Crown className="w-4 h-4" />;
      case UserRole.DEVELOPER: return <Edit3 className="w-4 h-4" />;
      default: return <Users className="w-4 h-4" />;
    }
  };

  const getRoleLabel = (role: UserRole) => {
    switch (role) {
      case UserRole.ADMIN: return 'Administrador';
      case UserRole.DEVELOPER: return 'Desenvolvedor';
      case UserRole.OPERATOR: return 'Operador';
      case UserRole.VIEWER: return 'Visualizador';
      default: return role;
    }
  };

  const availablePermissions: PermissionType[] = [
    'read_projects',
    'write_projects',
    'delete_projects',
    'manage_users',
    'manage_system',
    'deploy_applications',
    'view_monitoring',
    'manage_integrations'
  ];

  const formatPermission = (permission: string) => {
    return permission.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  return (
    <div className="settings-section">
      <div className="section-header">
        <h3>Gerenciamento de Usuários</h3>
        <div className="header-actions">
          <button className="btn btn-primary" onClick={() => setShowUserModal(true)}>
            <Plus className="w-4 h-4" />
            Novo Usuário
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'users' ? 'active' : ''}`}
          onClick={() => setActiveTab('users')}
        >
          <Users className="w-4 h-4" />
          Usuários ({users.length})
        </button>
        <button 
          className={`tab ${activeTab === 'roles' ? 'active' : ''}`}
          onClick={() => setActiveTab('roles')}
        >
          <Shield className="w-4 h-4" />
          Papéis ({roles.length})
        </button>
      </div>

      {activeTab === 'users' && (
        <div className="users-section">
          {/* Filtros */}
          <div className="filters">
            <div className="search-filter">
              <Search className="w-4 h-4" />
              <input
                type="text"
                placeholder="Buscar usuários..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <div className="role-filter">
              <Filter className="w-4 h-4" />
              <select value={roleFilter} onChange={(e) => setRoleFilter(e.target.value)}>
                <option value="">Todos os papéis</option>
                {Object.values(UserRole).map(role => (
                  <option key={role} value={role}>{getRoleLabel(role)}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Lista de Usuários */}
          <div className="users-grid">
            {filteredUsers.map(user => (
              <div key={user.id} className="user-card">
                <div className="user-header">
                  <div className="user-avatar">
                    {user.name.charAt(0).toUpperCase()}
                  </div>
                  <div className="user-info">
                    <h4>{user.name}</h4>
                    <p>{user.email}</p>
                  </div>
                  <div className="user-actions">
                    <button 
                      className="action-btn"
                      onClick={() => setSelectedUser(user)}
                    >
                      <MoreVertical className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                <div className="user-details">
                  <div className="detail-item">
                    <span className="detail-label">Papel:</span>
                    <div className="role-badge">
                      {getRoleIcon(user.role)}
                      {getRoleLabel(user.role)}
                    </div>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Status:</span>
                    <div className={`status-badge ${user.isActive ? 'active' : 'inactive'}`}>
                      {getStatusIcon(user.isActive)}
                      {user.isActive ? 'Ativo' : 'Inativo'}
                    </div>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Projetos:</span>
                    <span>{user.projects.length} projeto(s)</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Último acesso:</span>
                    <span>{user.lastLogin ? new Date(user.lastLogin).toLocaleDateString() : 'Nunca'}</span>
                  </div>
                </div>

                <div className="user-footer">
                  <button 
                    className="btn btn-sm btn-outline"
                    onClick={() => toggleUserStatus(user.id, user.isActive)}
                  >
                    {user.isActive ? 'Desativar' : 'Ativar'}
                  </button>
                  <button className="btn btn-sm btn-primary">
                    <Edit3 className="w-3 h-3" />
                    Editar
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'roles' && (
        <div className="roles-section">
          <div className="section-actions">
            <button className="btn btn-primary" onClick={() => setShowRoleModal(true)}>
              <Plus className="w-4 h-4" />
              Novo Papel
            </button>
          </div>

          <div className="roles-grid">
            {roles.map(role => (
              <div key={role.id} className="role-card">
                <div className="role-header">
                  <h4>{role.name}</h4>
                  <p>{role.description}</p>
                </div>
                <div className="role-permissions">
                  <h5>Permissões ({role.permissions.length})</h5>
                  <div className="permissions-list">
                    {role.permissions.map((permission) => (
                      <span key={permission} className="permission-badge">
                        {formatPermission(permission)}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="role-footer">
                  <span className="users-count">
                    {users.filter(u => u.role === role.name).length} usuários
                  </span>
                  <div className="role-actions">
                    <button className="btn btn-sm btn-outline">
                      <Edit3 className="w-3 h-3" />
                      Editar
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Modal Novo Usuário */}
      {showUserModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h3>Novo Usuário</h3>
              <button onClick={() => setShowUserModal(false)}>×</button>
            </div>
            <div className="modal-content">
              <div className="form-group">
                <label>Nome completo</label>
                <input
                  type="text"
                  value={newUser.name}
                  onChange={(e) => setNewUser({...newUser, name: e.target.value})}
                  placeholder="Digite o nome completo"
                />
              </div>
              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={newUser.email}
                  onChange={(e) => setNewUser({...newUser, email: e.target.value})}
                  placeholder="Digite o email"
                />
              </div>
              <div className="form-group">
                <label>Papel</label>
                <select
                  value={newUser.role}
                  onChange={(e) => setNewUser({...newUser, role: e.target.value as UserRole})}
                >
                  {Object.values(UserRole).map(role => (
                    <option key={role} value={role}>{getRoleLabel(role)}</option>
                  ))}
                </select>
              </div>
              <div className="form-group checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    checked={newUser.isActive}
                    onChange={(e) => setNewUser({...newUser, isActive: e.target.checked})}
                  />
                  Usuário ativo
                </label>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-outline" onClick={() => setShowUserModal(false)}>
                Cancelar
              </button>
              <button className="btn btn-primary" onClick={handleCreateUser}>
                Criar Usuário
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal Novo Papel */}
      {showRoleModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h3>Novo Papel</h3>
              <button onClick={() => setShowRoleModal(false)}>×</button>
            </div>
            <div className="modal-content">
              <div className="form-group">
                <label>Nome do papel</label>
                <input
                  type="text"
                  value={newRole.name}
                  onChange={(e) => setNewRole({...newRole, name: e.target.value})}
                  placeholder="Digite o nome do papel"
                />
              </div>
              <div className="form-group">
                <label>Descrição</label>
                <textarea
                  value={newRole.description}
                  onChange={(e) => setNewRole({...newRole, description: e.target.value})}
                  placeholder="Descreva as responsabilidades deste papel"
                  rows={3}
                />
              </div>
              <div className="form-group">
                <label>Permissões</label>
                <div className="permissions-checkboxes">
                  {availablePermissions.map((permission) => (
                    <label key={permission} className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={newRole.permissions.includes(permission)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setNewRole({
                              ...newRole,
                              permissions: [...newRole.permissions, permission]
                            });
                          } else {
                            setNewRole({
                              ...newRole,
                              permissions: newRole.permissions.filter(p => p !== permission)
                            });
                          }
                        }}
                      />
                      {formatPermission(permission)}
                    </label>
                  ))}
                </div>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-outline" onClick={() => setShowRoleModal(false)}>
                Cancelar
              </button>
              <button className="btn btn-primary" onClick={handleCreateRole}>
                Criar Papel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserManagement;