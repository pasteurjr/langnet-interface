// src/pages/McpServiceDiscoveryPage.tsx
import React, { useState, useEffect } from "react";
import { McpService, McpConnection, McpDiscoveryResult } from "../types";
import "./McpServiceDiscoveryPage.css";

const McpServiceDiscoveryPage: React.FC = () => {
  const [services, setServices] = useState<McpService[]>([
    {
      id: "auth_service_1",
      name: "AuthService",
      provider: "Corp Systems",
      version: "v2.1.0",
      status: "up",
      category: "auth",
      usage: "high",
      description: "Serviço de autenticação e autorização corporativo",
      endpoints: ["/auth/login", "/auth/verify", "/auth/refresh"],
      dependencies: ["NetworkStorage"],
      capabilities: ["JWT", "OAuth2", "SAML"],
      rateLimits: {
        requestsPerMinute: 1000,
        requestsPerHour: 50000,
      },
      sla: {
        uptime: 99.9,
        responseTime: 100,
      },
    },
    {
      id: "storage_service_1",
      name: "DataStore",
      provider: "Corp Systems",
      version: "v3.0.1",
      status: "up",
      category: "storage",
      usage: "high",
      description: "Serviço de armazenamento de dados persistente",
      endpoints: [
        "/store/create",
        "/store/query",
        "/store/update",
        "/store/delete",
      ],
      dependencies: ["AuthService", "NetworkStorage"],
      capabilities: ["SQL", "NoSQL", "Backup", "Encryption"],
      rateLimits: {
        requestsPerMinute: 500,
        requestsPerHour: 25000,
      },
      sla: {
        uptime: 99.8,
        responseTime: 150,
      },
    },
    {
      id: "ai_service_1",
      name: "MLModels",
      provider: "AI Corp",
      version: "v2.3.0",
      status: "slow",
      category: "ai",
      usage: "medium",
      description: "Serviços de Machine Learning e IA",
      endpoints: ["/ml/predict", "/ml/train", "/ml/models"],
      dependencies: ["DataStore"],
      capabilities: ["NLP", "Computer Vision", "Sentiment Analysis"],
      rateLimits: {
        requestsPerMinute: 100,
        requestsPerHour: 5000,
      },
      sla: {
        uptime: 98.5,
        responseTime: 500,
      },
    },
    {
      id: "comm_service_1",
      name: "Notifications",
      provider: "Comm Systems",
      version: "v2.0.0",
      status: "down",
      category: "communication",
      usage: "low",
      description: "Serviço de notificações e mensagens",
      endpoints: ["/notify/email", "/notify/sms", "/notify/push"],
      dependencies: ["AuthService"],
      capabilities: ["Email", "SMS", "Push Notifications", "Templates"],
      rateLimits: {
        requestsPerMinute: 200,
        requestsPerHour: 10000,
      },
      sla: {
        uptime: 95.0,
        responseTime: 200,
      },
    },
    {
      id: "search_service_1",
      name: "SearchEngine",
      provider: "Search Corp",
      version: "v1.5.3",
      status: "up",
      category: "other",
      usage: "medium",
      description: "Serviço de busca e indexação",
      endpoints: ["/search/query", "/search/index", "/search/suggest"],
      dependencies: ["DataStore"],
      capabilities: ["Full-text Search", "Faceted Search", "Auto-complete"],
      rateLimits: {
        requestsPerMinute: 300,
        requestsPerHour: 15000,
      },
      sla: {
        uptime: 99.5,
        responseTime: 80,
      },
    },
    {
      id: "analytics_service_1",
      name: "Analytics",
      provider: "Corp Systems",
      version: "v1.8.2",
      status: "up",
      category: "analytics",
      usage: "medium",
      description: "Serviço de análise e métricas",
      endpoints: [
        "/analytics/track",
        "/analytics/report",
        "/analytics/dashboard",
      ],
      dependencies: ["DataStore", "AuthService"],
      capabilities: ["Real-time Analytics", "Custom Reports", "Dashboards"],
      rateLimits: {
        requestsPerMinute: 400,
        requestsPerHour: 20000,
      },
      sla: {
        uptime: 99.2,
        responseTime: 120,
      },
    },
  ]);

  const [connections, setConnections] = useState<McpConnection[]>([
    {
      id: "conn_auth_001",
      serviceId: "auth_service_1",
      serviceName: "AuthService",
      status: "connected",
      latency: 23,
      lastActivity: "2025-05-27T14:30:00Z",
      requestsPerHour: 1245,
      errorRate: 0.01,
    },
    {
      id: "conn_storage_002",
      serviceId: "storage_service_1",
      serviceName: "DataStore",
      status: "connected",
      latency: 45,
      lastActivity: "2025-05-27T14:29:45Z",
      requestsPerHour: 856,
      errorRate: 0.02,
    },
    {
      id: "conn_ai_003",
      serviceId: "ai_service_1",
      serviceName: "MLModels",
      status: "error",
      latency: 0,
      lastActivity: "2025-05-27T13:45:30Z",
      requestsPerHour: 0,
      errorRate: 1.0,
    },
    {
      id: "conn_search_004",
      serviceId: "search_service_1",
      serviceName: "SearchEngine",
      status: "connected",
      latency: 67,
      lastActivity: "2025-05-27T14:29:50Z",
      requestsPerHour: 423,
      errorRate: 0.005,
    },
  ]);

  const [selectedService, setSelectedService] = useState<McpService | null>(
    null
  );
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [filterCategory, setFilterCategory] = useState<string>("all");
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [discoveryResult, setDiscoveryResult] = useState<McpDiscoveryResult>({
    totalServices: 47,
    onlineServices: 42,
    lastScan: "2025-05-27T14:29:00Z",
    networkHealth: 98.7,
    avgLatency: 23,
    servicesByCategory: {
      auth: 8,
      storage: 12,
      ai: 15,
      communication: 6,
      analytics: 4,
      other: 2,
    },
    usageStats: {},
  });

  const filteredServices = services.filter((service) => {
    const matchesStatus =
      filterStatus === "all" || service.status === filterStatus;
    const matchesCategory =
      filterCategory === "all" || service.category === filterCategory;
    const searchLower = (searchTerm || "").toLowerCase();
    const matchesSearch =
      searchTerm === "" ||
      service.name.toLowerCase().includes(searchLower) ||
      (service.description || "").toLowerCase().includes(searchLower);

    return matchesStatus && matchesCategory && matchesSearch;
  });

  const handleRefreshServices = () => {
    console.log("Refreshing service discovery...");
    setDiscoveryResult((prev) => ({
      ...prev,
      lastScan: new Date().toISOString(),
    }));
  };

  const handleServiceAction = (serviceId: string, action: string) => {
    console.log(`Action ${action} for service ${serviceId}`);
    switch (action) {
      case "connect":
        // Implementar conexão com o serviço
        break;
      case "test":
        // Implementar teste do serviço
        break;
      case "monitor":
        // Implementar monitoramento
        break;
      case "disconnect":
        setConnections((prev) =>
          prev.filter((conn) => conn.serviceId !== serviceId)
        );
        break;
      default:
        break;
    }
  };

  const handleBulkConnect = () => {
    console.log("Bulk connecting to services...");
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "up":
        return "🟢";
      case "down":
        return "❌";
      case "slow":
        return "🟡";
      case "maintenance":
        return "🔧";
      default:
        return "⚪";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "up":
        return "#22c55e";
      case "down":
        return "#ef4444";
      case "slow":
        return "#eab308";
      case "maintenance":
        return "#8b5cf6";
      default:
        return "#6b7280";
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case "auth":
        return "🔐";
      case "storage":
        return "💾";
      case "ai":
        return "🤖";
      case "communication":
        return "📧";
      case "analytics":
        return "📊";
      default:
        return "⚙️";
    }
  };

  const getUsageColor = (usage: string) => {
    switch (usage) {
      case "high":
        return "#ef4444";
      case "medium":
        return "#eab308";
      case "low":
        return "#22c55e";
      case "none":
        return "#6b7280";
      default:
        return "#6b7280";
    }
  };

  return (
    <div className="mcp-service-discovery-container">
      <div className="page-header">
        <h1>Descoberta de Serviços MCP</h1>
        <div className="header-actions">
          <button className="btn-secondary" onClick={handleRefreshServices}>
            🔄 Atualizar
          </button>
          <button className="btn-primary" onClick={handleBulkConnect}>
            🔗 Conectar em Massa
          </button>
        </div>
      </div>

      {/* Discovery Overview */}
      <section className="discovery-overview">
        <div className="overview-cards">
          <div className="overview-card">
            <div className="card-icon">🌐</div>
            <div className="card-info">
              <h3>{discoveryResult.totalServices}</h3>
              <p>Serviços Descobertos</p>
            </div>
          </div>
          <div className="overview-card">
            <div className="card-icon">🟢</div>
            <div className="card-info">
              <h3>{discoveryResult.onlineServices}</h3>
              <p>Online</p>
            </div>
          </div>
          <div className="overview-card">
            <div className="card-icon">⚡</div>
            <div className="card-info">
              <h3>{discoveryResult.avgLatency}ms</h3>
              <p>Latência Média</p>
            </div>
          </div>
          <div className="overview-card">
            <div className="card-icon">💚</div>
            <div className="card-info">
              <h3>{discoveryResult.networkHealth}%</h3>
              <p>Saúde da Rede</p>
            </div>
          </div>
        </div>
        <div className="last-scan">
          Última varredura:{" "}
          {new Date(discoveryResult.lastScan).toLocaleString("pt-BR")}
        </div>
      </section>

      {/* Filters and Search */}
      <section className="filters-section">
        <div className="filters-bar">
          <div className="search-group">
            <input
              type="text"
              placeholder="Buscar serviços..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
          </div>

          <div className="filter-group">
            <label>Status:</label>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
            >
              <option value="all">Todos</option>
              <option value="up">Online</option>
              <option value="down">Offline</option>
              <option value="slow">Lento</option>
              <option value="maintenance">Manutenção</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Categoria:</label>
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
            >
              <option value="all">Todas</option>
              <option value="auth">Autenticação</option>
              <option value="storage">Armazenamento</option>
              <option value="ai">IA/ML</option>
              <option value="communication">Comunicação</option>
              <option value="analytics">Analytics</option>
              <option value="other">Outros</option>
            </select>
          </div>
        </div>
      </section>

      <div className="content-layout">
        {/* Services List */}
        <section className="services-section">
          <div className="section-header">
            <h2>Serviços Disponíveis ({filteredServices.length})</h2>
          </div>

          <div className="services-table">
            <table>
              <thead>
                <tr>
                  <th>Serviço</th>
                  <th>Versão</th>
                  <th>Status</th>
                  <th>Uso</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody>
                {filteredServices.map((service) => (
                  <tr
                    key={service.id}
                    className={
                      selectedService?.id === service.id ? "selected" : ""
                    }
                    onClick={() => setSelectedService(service)}
                  >
                    <td>
                      <div className="service-info">
                        <div className="service-header">
                          <span className="service-icon">
                            {getCategoryIcon(service.category)}
                          </span>
                          <span className="service-name">{service.name}</span>
                        </div>
                        <div className="service-provider">
                          {service.provider}
                        </div>
                        {service.description && (
                          <div className="service-description">
                            {service.description}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="service-version">{service.version}</td>
                    <td>
                      <span
                        className="status-badge"
                        style={{
                          backgroundColor: getStatusColor(service.status),
                        }}
                      >
                        {getStatusIcon(service.status)} {service.status}
                      </span>
                    </td>
                    <td>
                      <span
                        className="usage-badge"
                        style={{
                          color: getUsageColor(service.usage || "none"),
                        }}
                      >
                        {service.usage || "N/A"}
                      </span>
                    </td>
                    <td>
                      <div className="action-buttons">
                        <button
                          className="btn-icon"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleServiceAction(service.id, "connect");
                          }}
                          title="Conectar"
                        >
                          🔗
                        </button>
                        <button
                          className="btn-icon"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleServiceAction(service.id, "test");
                          }}
                          title="Testar"
                        >
                          🧪
                        </button>
                        <button
                          className="btn-icon"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleServiceAction(service.id, "monitor");
                          }}
                          title="Monitorar"
                        >
                          📊
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Service Details Panel */}
        {selectedService && (
          <section className="service-details">
            <div className="details-header">
              <div className="service-title">
                <span className="service-icon">
                  {getCategoryIcon(selectedService.category)}
                </span>
                <div>
                  <h3>{selectedService.name}</h3>
                  <p>{selectedService.description}</p>
                </div>
              </div>
              <button
                className="btn-close"
                onClick={() => setSelectedService(null)}
              >
                ×
              </button>
            </div>

            <div className="details-content">
              <div className="detail-section">
                <h4>Informações Gerais</h4>
                <div className="detail-grid">
                  <div className="detail-item">
                    <span className="detail-label">Provedor:</span>
                    <span className="detail-value">
                      {selectedService.provider}
                    </span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Versão:</span>
                    <span className="detail-value">
                      {selectedService.version}
                    </span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Categoria:</span>
                    <span className="detail-value">
                      {getCategoryIcon(selectedService.category)}{" "}
                      {selectedService.category}
                    </span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Status:</span>
                    <span
                      className="status-badge small"
                      style={{
                        backgroundColor: getStatusColor(selectedService.status),
                      }}
                    >
                      {getStatusIcon(selectedService.status)}{" "}
                      {selectedService.status}
                    </span>
                  </div>
                </div>
              </div>

              {selectedService.endpoints && (
                <div className="detail-section">
                  <h4>Endpoints da API</h4>
                  <ul className="endpoints-list">
                    {selectedService.endpoints.map((endpoint, index) => (
                      <li key={index} className="endpoint-item">
                        <code>
                          {typeof endpoint === "string"
                            ? endpoint
                            : endpoint.path}
                        </code>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {selectedService.capabilities && (
                <div className="detail-section">
                  <h4>Capacidades</h4>
                  <div className="capabilities-list">
                    {selectedService.capabilities.map((capability, index) => (
                      <span key={index} className="capability-tag">
                        {capability}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {selectedService.rateLimits && (
                <div className="detail-section">
                  <h4>Limites de Taxa</h4>
                  <div className="detail-grid">
                    <div className="detail-item">
                      <span className="detail-label">Por minuto:</span>
                      <span className="detail-value">
                        {selectedService.rateLimits.requestsPerMinute} req/min
                      </span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Por hora:</span>
                      <span className="detail-value">
                        {selectedService.rateLimits.requestsPerHour} req/h
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {selectedService.sla && (
                <div className="detail-section">
                  <h4>SLA</h4>
                  <div className="detail-grid">
                    <div className="detail-item">
                      <span className="detail-label">Uptime:</span>
                      <span className="detail-value">
                        {selectedService.sla.uptime}%
                      </span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Tempo de Resposta:</span>
                      <span className="detail-value">
                        {selectedService.sla.responseTime}ms
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {selectedService.dependencies &&
                selectedService.dependencies.length > 0 && (
                  <div className="detail-section">
                    <h4>Dependências</h4>
                    <div className="dependencies-list">
                      {selectedService.dependencies.map((dep, index) => (
                        <span key={index} className="dependency-tag">
                          {dep}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

              <div className="detail-actions">
                <button
                  className="btn-primary"
                  onClick={() =>
                    handleServiceAction(selectedService.id, "connect")
                  }
                >
                  🔗 Conectar
                </button>
                <button
                  className="btn-secondary"
                  onClick={() =>
                    handleServiceAction(selectedService.id, "test")
                  }
                >
                  🧪 Testar
                </button>
                <button
                  className="btn-secondary"
                  onClick={() =>
                    handleServiceAction(selectedService.id, "documentation")
                  }
                >
                  📚 Documentação
                </button>
                <button
                  className="btn-secondary"
                  onClick={() =>
                    handleServiceAction(selectedService.id, "monitor")
                  }
                >
                  📊 Monitorar
                </button>
              </div>
            </div>
          </section>
        )}
      </div>

      {/* Active Connections */}
      <section className="connections-section">
        <div className="section-header">
          <h2>Conexões Ativas</h2>
        </div>

        <div className="connections-table">
          <table>
            <thead>
              <tr>
                <th>ID da Conexão</th>
                <th>Serviço</th>
                <th>Status</th>
                <th>Latência</th>
                <th>Última Atividade</th>
                <th>Req/h</th>
                <th>Taxa de Erro</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              {connections.map((connection) => (
                <tr key={connection.id}>
                  <td className="connection-id">{connection.id}</td>
                  <td className="service-name">{connection.serviceName}</td>
                  <td>
                    <span
                      className="status-badge"
                      style={{
                        backgroundColor:
                          connection.status === "connected"
                            ? "#22c55e"
                            : connection.status === "error"
                            ? "#ef4444"
                            : "#6b7280",
                      }}
                    >
                      {connection.status === "connected" && "🟢"}
                      {connection.status === "error" && "❌"}
                      {connection.status === "connecting" && "🟡"}
                      {connection.status === "disconnected" && "⚪"}
                      {connection.status}
                    </span>
                  </td>
                  <td>{connection.latency}ms</td>
                  <td>
                    {connection.lastActivity
                      ? new Date(connection.lastActivity).toLocaleString(
                          "pt-BR"
                        )
                      : "N/A"}
                  </td>
                  <td>{connection.requestsPerHour || 0}</td>
                  <td>
                    <span
                      style={{
                        color:
                          (connection.errorRate || 0) > 0.1
                            ? "#ef4444"
                            : "#22c55e",
                      }}
                    >
                      {((connection.errorRate || 0) * 100).toFixed(2)}%
                    </span>
                  </td>
                  <td>
                    <div className="action-buttons">
                      <button
                        className="btn-icon"
                        onClick={() =>
                          handleServiceAction(
                            connection.serviceId,
                            "disconnect"
                          )
                        }
                        title="Desconectar"
                      >
                        🔌
                      </button>
                      <button
                        className="btn-icon"
                        onClick={() =>
                          handleServiceAction(connection.serviceId, "monitor")
                        }
                        title="Monitorar"
                      >
                        📊
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Version Compatibility Matrix */}
      <section className="compatibility-section">
        <div className="section-header">
          <h2>Matriz de Compatibilidade de Versões</h2>
        </div>

        <div className="compatibility-table">
          <table>
            <thead>
              <tr>
                <th>Serviço</th>
                <th>Versão Atual</th>
                <th>Versões Suportadas</th>
                <th>Versões Depreciadas</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>AuthService</td>
                <td>v2.1.0</td>
                <td>v2.0+</td>
                <td>v1.x (EOL)</td>
                <td>
                  <span className="compatibility-ok">✅ Compatível</span>
                </td>
              </tr>
              <tr>
                <td>DataStore</td>
                <td>v3.0.1</td>
                <td>v2.5+</td>
                <td>v2.0-v2.4</td>
                <td>
                  <span className="compatibility-ok">✅ Compatível</span>
                </td>
              </tr>
              <tr>
                <td>MLModels</td>
                <td>v2.3.0</td>
                <td>v2.0+</td>
                <td>v1.x (EOL)</td>
                <td>
                  <span className="compatibility-warning">
                    ⚠️ Update Recomendado
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      {/* Action Buttons */}
      <div className="page-actions">
        <button
          className="btn-secondary"
          onClick={() => console.log("Export registry")}
        >
          📤 Exportar Registry
        </button>
        <button
          className="btn-secondary"
          onClick={() => console.log("Import services")}
        >
          📥 Importar Serviços
        </button>
        <button className="btn-primary" onClick={handleRefreshServices}>
          🔄 Atualizar Discovery
        </button>
      </div>
    </div>
  );
};

export default McpServiceDiscoveryPage;
