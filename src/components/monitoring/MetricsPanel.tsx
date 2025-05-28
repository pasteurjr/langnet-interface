import React from 'react';
import { BarChart3, TrendingUp, DollarSign, Zap, Clock, CheckCircle, AlertTriangle } from 'lucide-react';
import { MonitoringMetrics } from '../../types/monitoring';
import './monitoring.css';

interface MetricsPanelProps {
  metrics: MonitoringMetrics;
  timeRange: '1h' | '24h' | '7d' | '30d';
  onTimeRangeChange: (range: '1h' | '24h' | '7d' | '30d') => void;
}

export const MetricsPanel: React.FC<MetricsPanelProps> = ({
  metrics,
  timeRange,
  onTimeRangeChange
}) => {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  };

  const formatNumber = (value: number) => {
    return new Intl.NumberFormat('pt-BR').format(value);
  };

  const formatPercentage = (value: number) => {
    return `${value.toFixed(1)}%`;
  };

  const getTimeRangeLabel = (range: string) => {
    switch (range) {
      case '1h': return 'Última hora';
      case '24h': return 'Últimas 24h';
      case '7d': return 'Últimos 7 dias';
      case '30d': return 'Últimos 30 dias';
      default: return range;
    }
  };

  const calculateAvgTokensPerTrace = () => {
    if (metrics.totalTraces === 0) return 0;
    return (metrics.totalTokens / metrics.totalTraces).toFixed(1);
  };

  const calculateAvgCostPerTrace = () => {
    if (metrics.totalTraces === 0) return 0;
    return (metrics.totalCost / metrics.totalTraces).toFixed(4);
  };

  const calculateAvgSpansPerTrace = () => {
    if (metrics.totalTraces === 0) return 0;
    return (metrics.totalSpans / metrics.totalTraces).toFixed(1);
  };

  const calculateAvgGenerationsPerTrace = () => {
    if (metrics.totalTraces === 0) return 0;
    return (metrics.totalGenerations / metrics.totalTraces).toFixed(1);
  };

  return (
    <div className="metrics-panel">
      <div className="metrics-header">
        <h4>Métricas do Sistema</h4>
        <select 
          value={timeRange} 
          onChange={(e) => onTimeRangeChange(e.target.value as any)}
          className="time-range-selector"
        >
          <option value="1h">Última hora</option>
          <option value="24h">Últimas 24h</option>
          <option value="7d">Últimos 7 dias</option>
          <option value="30d">Últimos 30 dias</option>
        </select>
      </div>

      <div className="metrics-summary">
        <div className="metric-summary-item">
          <div className="metric-icon">
            <BarChart3 size={16} color="#4a90e2" />
          </div>
          <div className="metric-content">
            <div className="metric-summary-value">{formatNumber(metrics.totalTraces)}</div>
            <div className="metric-summary-label">Total Traces</div>
          </div>
        </div>

        <div className="metric-summary-item">
          <div className="metric-icon">
            <Zap size={16} color="#f59e0b" />
          </div>
          <div className="metric-content">
            <div className="metric-summary-value">{formatNumber(metrics.totalTokens)}</div>
            <div className="metric-summary-label">Tokens</div>
          </div>
        </div>

        <div className="metric-summary-item">
          <div className="metric-icon">
            <DollarSign size={16} color="#16a34a" />
          </div>
          <div className="metric-content">
            <div className="metric-summary-value">{formatCurrency(metrics.totalCost)}</div>
            <div className="metric-summary-label">Custo</div>
          </div>
        </div>

        <div className="metric-summary-item">
          <div className="metric-icon">
            <Clock size={16} color="#8b5cf6" />
          </div>
          <div className="metric-content">
            <div className="metric-summary-value">{metrics.averageLatency}s</div>
            <div className="metric-summary-label">Latência Média</div>
          </div>
        </div>
      </div>

      <div className="metrics-details">
        <div className="metrics-row">
          <div className="metric-detail-item">
            <div className="metric-detail-header">
              <CheckCircle size={16} color="#16a34a" />
              <span>Taxa de Sucesso</span>
            </div>
            <div className="metric-detail-value success">
              {formatPercentage(metrics.successRate)}
            </div>
            <div className="metric-detail-description">
              {formatNumber(Math.round(metrics.totalTraces * metrics.successRate / 100))} traces bem-sucedidos
            </div>
          </div>

          <div className="metric-detail-item">
            <div className="metric-detail-header">
              <AlertTriangle size={16} color="#dc2626" />
              <span>Taxa de Erro</span>
            </div>
            <div className="metric-detail-value error">
              {formatPercentage(metrics.errorRate)}
            </div>
            <div className="metric-detail-description">
              {formatNumber(Math.round(metrics.totalTraces * metrics.errorRate / 100))} traces com erro
            </div>
          </div>
        </div>

        <div className="metrics-row">
          <div className="metric-detail-item">
            <div className="metric-detail-header">
              <BarChart3 size={16} color="#4a90e2" />
              <span>Spans Processados</span>
            </div>
            <div className="metric-detail-value">
              {formatNumber(metrics.totalSpans)}
            </div>
            <div className="metric-detail-description">
              Média de {calculateAvgSpansPerTrace()} spans por trace
            </div>
          </div>

          <div className="metric-detail-item">
            <div className="metric-detail-header">
              <TrendingUp size={16} color="#f59e0b" />
              <span>Gerações LLM</span>
            </div>
            <div className="metric-detail-value">
              {formatNumber(metrics.totalGenerations)}
            </div>
            <div className="metric-detail-description">
              Média de {calculateAvgGenerationsPerTrace()} gerações por trace
            </div>
          </div>
        </div>

        <div className="metrics-row">
          <div className="metric-detail-item">
            <div className="metric-detail-header">
              <Zap size={16} color="#f59e0b" />
              <span>Tokens por Trace</span>
            </div>
            <div className="metric-detail-value">
              {calculateAvgTokensPerTrace()}
            </div>
            <div className="metric-detail-description">
              Consumo médio de tokens por execução
            </div>
          </div>

          <div className="metric-detail-item">
            <div className="metric-detail-header">
              <DollarSign size={16} color="#16a34a" />
              <span>Custo por Trace</span>
            </div>
            <div className="metric-detail-value">
              ${calculateAvgCostPerTrace()}
            </div>
            <div className="metric-detail-description">
              Custo médio por execução de trace
            </div>
          </div>
        </div>
      </div>

      <div className="metrics-efficiency">
        <h5>Indicadores de Eficiência</h5>
        <div className="efficiency-grid">
          <div className="efficiency-item">
            <div className="efficiency-label">Throughput</div>
            <div className="efficiency-value">
              {(metrics.totalTraces / 24).toFixed(1)} traces/hora
            </div>
            <div className="efficiency-description">
              Taxa de processamento média
            </div>
          </div>

          <div className="efficiency-item">
            <div className="efficiency-label">Eficiência de Tokens</div>
            <div className="efficiency-value">
              {metrics.totalTokens > 0 ? ((metrics.totalGenerations / metrics.totalTokens) * 1000).toFixed(2) : '0'} ger/k tokens
            </div>
            <div className="efficiency-description">
              Gerações por mil tokens
            </div>
          </div>

          <div className="efficiency-item">
            <div className="efficiency-label">Relação Custo/Benefício</div>
            <div className="efficiency-value">
              {metrics.totalCost > 0 ? (metrics.successRate / metrics.totalCost).toFixed(1) : '0'} %/USD
            </div>
            <div className="efficiency-description">
              Taxa de sucesso por dólar gasto
            </div>
          </div>

          <div className="efficiency-item">
            <div className="efficiency-label">Performance</div>
            <div className="efficiency-value performance-score">
              {((metrics.successRate + (100 - metrics.averageLatency * 10)) / 2).toFixed(0)}%
            </div>
            <div className="efficiency-description">
              Score combinado de sucesso e velocidade
            </div>
          </div>
        </div>
      </div>

      <div className="metrics-comparison">
        <h5>Comparativo Temporal</h5>
        <div className="comparison-grid">
          <div className="comparison-item">
            <div className="comparison-metric">Volume de Traces</div>
            <div className="comparison-trend positive">
              <TrendingUp size={14} />
              +15.2% vs período anterior
            </div>
          </div>

          <div className="comparison-item">
            <div className="comparison-metric">Custo Total</div>
            <div className="comparison-trend negative">
              <TrendingUp size={14} />
              +8.7% vs período anterior
            </div>
          </div>

          <div className="comparison-item">
            <div className="comparison-metric">Taxa de Sucesso</div>
            <div className="comparison-trend positive">
              <TrendingUp size={14} />
              +2.1% vs período anterior
            </div>
          </div>

          <div className="comparison-item">
            <div className="comparison-metric">Latência Média</div>
            <div className="comparison-trend positive">
              <TrendingUp size={14} />
              -0.3s vs período anterior
            </div>
          </div>
        </div>
      </div>

      <div className="metrics-period">
        <div className="period-info">
          <span className="period-label">Período analisado:</span>
          <span className="period-value">{getTimeRangeLabel(timeRange)}</span>
        </div>
        <div className="period-range">
          <span className="period-start">
            {new Date(metrics.timeRange.start).toLocaleDateString('pt-BR')}
          </span>
          <span className="period-separator">até</span>
          <span className="period-end">
            {new Date(metrics.timeRange.end).toLocaleDateString('pt-BR')}
          </span>
        </div>
      </div>

      <div className="metrics-recommendations">
        <h5>Recomendações</h5>
        <div className="recommendations-list">
          {metrics.errorRate > 5 && (
            <div className="recommendation warning">
              <AlertTriangle size={16} />
              <div className="recommendation-content">
                <div className="recommendation-title">Taxa de erro elevada</div>
                <div className="recommendation-text">
                  Taxa de erro de {formatPercentage(metrics.errorRate)} está acima do recomendado (5%). 
                  Considere revisar os prompts e tratamento de exceções.
                </div>
              </div>
            </div>
          )}

          {metrics.averageLatency > 10 && (
            <div className="recommendation warning">
              <Clock size={16} />
              <div className="recommendation-content">
                <div className="recommendation-title">Latência alta</div>
                <div className="recommendation-text">
                  Latência média de {metrics.averageLatency}s está alta. 
                  Considere otimizar prompts ou usar modelos mais rápidos.
                </div>
              </div>
            </div>
          )}

          {metrics.totalCost > 100 && (
            <div className="recommendation info">
              <DollarSign size={16} />
              <div className="recommendation-content">
                <div className="recommendation-title">Monitorar custos</div>
                <div className="recommendation-text">
                  Custo total de {formatCurrency(metrics.totalCost)} no período. 
                  Considere implementar cache para consultas frequentes.
                </div>
              </div>
            </div>
          )}

          {metrics.successRate > 95 && metrics.averageLatency < 5 && (
            <div className="recommendation success">
              <CheckCircle size={16} />
              <div className="recommendation-content">
                <div className="recommendation-title">Performance excelente</div>
                <div className="recommendation-text">
                  Sistema operando com alta eficiência: {formatPercentage(metrics.successRate)} sucesso 
                  e {metrics.averageLatency}s latência média.
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};