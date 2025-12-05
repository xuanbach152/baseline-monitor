import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  AlertTriangle, 
  RefreshCw, 
  Shield, 
  CheckCircle, 
  Clock,
  Activity,
  XCircle
} from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';
import './ViolationsPage.css';

const API_URL = import.meta.env.VITE_API_URL;

export default function ViolationsPage() {
  const [violations, setViolations] = useState([]);
  const [agents, setAgents] = useState([]);
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { theme } = useTheme();

  // Filters
  const [filterSeverity, setFilterSeverity] = useState('all');
  const [filterAgent, setFilterAgent] = useState('all');
  const [filterRule, setFilterRule] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all'); // all, resolved, unresolved
  const [searchQuery, setSearchQuery] = useState('');

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(20);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [violationsRes, agentsRes, rulesRes] = await Promise.all([
        axios.get(`${API_URL}/violations?limit=1000`),
        axios.get(`${API_URL}/agents?limit=1000`),
        axios.get(`${API_URL}/rules`),
      ]);

      setViolations(violationsRes.data || []);
      setAgents(agentsRes.data || []);
      setRules(rulesRes.data || []);
    } catch (err) {
      setError('Failed to load violations');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity) => {
    const sev = (severity || '').toLowerCase();
    if (sev === 'critical') return '#d32f2f';
    if (sev === 'high') return '#ff1744';
    if (sev === 'medium') return '#ffd600';
    if (sev === 'low') return '#4fd1c5';
    return '#b0b3b8';
  };

  const getSeverityIcon = (severity) => {
    const sev = (severity || '').toLowerCase();
    const iconProps = { size: 14, style: { display: 'inline', verticalAlign: 'middle' } };
    if (sev === 'critical') return <XCircle {...iconProps} />;
    if (sev === 'high') return <AlertTriangle {...iconProps} />;
    if (sev === 'medium') return <Clock {...iconProps} />;
    if (sev === 'low') return <Shield {...iconProps} />;
    return <Activity {...iconProps} />;
  };

  // Filter violations
  const filteredViolations = violations.filter((violation) => {
    // Get rule for severity check
    const rule = rules.find(r => r.id === violation.rule_id);
    const ruleSeverity = rule?.severity?.toLowerCase() || '';

    // Filter by severity
    if (filterSeverity !== 'all' && ruleSeverity !== filterSeverity) return false;

    // Filter by agent
    if (filterAgent !== 'all' && violation.agent_id !== parseInt(filterAgent)) return false;

    // Filter by rule
    if (filterRule !== 'all' && violation.rule_id !== filterRule) return false;

    // Filter by status
    if (filterStatus === 'resolved' && !violation.resolved_at) return false;
    if (filterStatus === 'unresolved' && violation.resolved_at) return false;

    // Search
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      const agentName = agents.find(a => a.id === violation.agent_id)?.hostname?.toLowerCase() || '';
      const ruleName = rule?.name?.toLowerCase() || '';
      const message = (violation.message || '').toLowerCase();
      
      if (!agentName.includes(query) && !ruleName.includes(query) && !message.includes(query)) {
        return false;
      }
    }

    return true;
  });

  // Pagination
  const totalPages = Math.ceil(filteredViolations.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedViolations = filteredViolations.slice(startIndex, startIndex + itemsPerPage);

  // Stats
  const stats = {
    total: violations.length,
    resolved: violations.filter(v => v.resolved_at).length,
    unresolved: violations.filter(v => !v.resolved_at).length,
    bySeverity: {
      critical: violations.filter(v => {
        const rule = rules.find(r => r.id === v.rule_id);
        return rule?.severity?.toLowerCase() === 'critical';
      }).length,
      high: violations.filter(v => {
        const rule = rules.find(r => r.id === v.rule_id);
        return rule?.severity?.toLowerCase() === 'high';
      }).length,
      medium: violations.filter(v => {
        const rule = rules.find(r => r.id === v.rule_id);
        return rule?.severity?.toLowerCase() === 'medium';
      }).length,
      low: violations.filter(v => {
        const rule = rules.find(r => r.id === v.rule_id);
        return rule?.severity?.toLowerCase() === 'low';
      }).length,
    },
  };

  if (loading) {
    return (
      <div className={`violations-page ${theme === 'light' ? 'light-mode' : ''}`}>
        <div className="page-header">
          <h1><AlertTriangle size={32} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 12 }} />Violations</h1>
        </div>
        <div className="loading"><Activity size={24} /> Loading violations...</div>
      </div>
    );
  }

  return (
    <div className={`violations-page ${theme === 'light' ? 'light-mode' : ''}`}>
      {/* HEADER */}
      <div className="page-header">
        <h1><AlertTriangle size={32} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 12 }} />Violations</h1>
        <button className="btn-primary" onClick={fetchData}>
          <RefreshCw size={16} /> Refresh
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {/* STATS */}
      <div className="violations-stats">
        <div className="stat-box">
          <div className="stat-value">{stats.total}</div>
          <div className="stat-label">Total</div>
        </div>
        <div className="stat-box unresolved">
          <div className="stat-value">{stats.unresolved}</div>
          <div className="stat-label">Unresolved</div>
        </div>
        <div className="stat-box resolved">
          <div className="stat-value">{stats.resolved}</div>
          <div className="stat-label">Resolved</div>
        </div>
        <div className="stat-box critical">
          <div className="stat-value">{stats.bySeverity.critical}</div>
          <div className="stat-label">Critical</div>
        </div>
        <div className="stat-box high">
          <div className="stat-value">{stats.bySeverity.high}</div>
          <div className="stat-label">High</div>
        </div>
        <div className="stat-box medium">
          <div className="stat-value">{stats.bySeverity.medium}</div>
          <div className="stat-label">Medium</div>
        </div>
      </div>

      {/* FILTERS */}
      <div className="filters-bar">
        <div className="filter-group">
          <label>Severity:</label>
          <select value={filterSeverity} onChange={(e) => setFilterSeverity(e.target.value)}>
            <option value="all">All</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Agent:</label>
          <select value={filterAgent} onChange={(e) => setFilterAgent(e.target.value)}>
            <option value="all">All Agents</option>
            {agents.map(agent => (
              <option key={agent.id} value={agent.id}>
                {agent.hostname}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>Rule:</label>
          <select value={filterRule} onChange={(e) => setFilterRule(e.target.value)}>
            <option value="all">All Rules</option>
            {rules.map(rule => (
              <option key={rule.id} value={rule.id}>
                {rule.name}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>Status:</label>
          <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
            <option value="all">All</option>
            <option value="unresolved">Unresolved</option>
            <option value="resolved">Resolved</option>
          </select>
        </div>

        <div className="filter-group search-group">
          <label>Search:</label>
          <input
            type="text"
            placeholder="Search violations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* VIOLATIONS TABLE */}
      <div className="violations-table-container">
        <table className="violations-table">
          <thead>
            <tr>
              <th>Time</th>
              <th>Severity</th>
              <th>Agent</th>
              <th>Rule</th>
              <th>Message</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {paginatedViolations.length === 0 ? (
              <tr>
                <td colSpan={6} className="empty-state">
                  <AlertTriangle size={24} style={{ opacity: 0.3, marginRight: 8 }} />
                  No violations found matching your criteria
                </td>
              </tr>
            ) : (
              paginatedViolations.map((violation) => {
                const agent = agents.find(a => a.id === violation.agent_id);
                const rule = rules.find(r => r.id === violation.rule_id);
                const severity = rule?.severity?.toLowerCase() || 'unknown';

                return (
                  <tr key={violation.id} className={violation.resolved_at ? 'resolved' : ''}>
                    <td className="time-cell">
                      {new Date(violation.detected_at).toLocaleString()}
                    </td>
                    <td className="severity-cell">
                      <span
                        className="severity-badge"
                        style={{
                          background: `${getSeverityColor(severity)}22`,
                          color: getSeverityColor(severity),
                          border: `2px solid ${getSeverityColor(severity)}`,
                        }}
                      >
                        {getSeverityIcon(severity)} {severity.toUpperCase()}
                      </span>
                    </td>
                    <td className="agent-cell">
                      {agent?.hostname || `Agent #${violation.agent_id}`}
                    </td>
                    <td className="rule-cell">
                      {rule?.name || violation.rule_id}
                    </td>
                    <td className="message-cell">
                      <div className="message-text" title={violation.message}>
                        {violation.message}
                      </div>
                    </td>
                    <td className="status-cell">
                      {violation.resolved_at ? (
                        <span className="status-badge resolved"><CheckCircle size={14} /> Resolved</span>
                      ) : (
                        <span className="status-badge unresolved"><Clock size={14} /> Open</span>
                      )}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* PAGINATION */}
      {totalPages > 1 && (
        <div className="pagination">
          <button
            className="page-btn"
            onClick={() => setCurrentPage(1)}
            disabled={currentPage === 1}
          >
            ««
          </button>
          <button
            className="page-btn"
            onClick={() => setCurrentPage(currentPage - 1)}
            disabled={currentPage === 1}
          >
            «
          </button>
          
          <span className="page-info">
            Page {currentPage} of {totalPages} ({filteredViolations.length} violations)
          </span>
          
          <button
            className="page-btn"
            onClick={() => setCurrentPage(currentPage + 1)}
            disabled={currentPage === totalPages}
          >
            »
          </button>
          <button
            className="page-btn"
            onClick={() => setCurrentPage(totalPages)}
            disabled={currentPage === totalPages}
          >
            »»
          </button>
        </div>
      )}
    </div>
  );
}
