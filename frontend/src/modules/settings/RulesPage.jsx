import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './RulesPage.css';

const API_URL = import.meta.env.VITE_API_URL;

export default function RulesPage() {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedRule, setSelectedRule] = useState(null);

  // Filters
  const [filterOS, setFilterOS] = useState('all'); // all, ubuntu, windows
  const [filterSeverity, setFilterSeverity] = useState('all');
  const [filterCategory, setFilterCategory] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all'); // all, active, inactive
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchRules();
  }, []);

  const fetchRules = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(`${API_URL}/rules`);
      setRules(res.data || []);
    } catch (err) {
      setError('Failed to load rules');
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
    if (sev === 'critical') return '🔴';
    if (sev === 'high') return '🟠';
    if (sev === 'medium') return '🟡';
    if (sev === 'low') return '🟢';
    return '⚪';
  };

  // Get unique categories
  const categories = [...new Set(rules.map(r => r.category).filter(Boolean))];

  // Filter rules
  const filteredRules = rules.filter((rule) => {
    // Filter by OS
    if (filterOS !== 'all' && rule.os_type !== filterOS) return false;

    // Filter by severity
    if (filterSeverity !== 'all' && rule.severity?.toLowerCase() !== filterSeverity) return false;

    // Filter by category
    if (filterCategory !== 'all' && rule.category !== filterCategory) return false;

    // Filter by status
    if (filterStatus === 'active' && !rule.active) return false;
    if (filterStatus === 'inactive' && rule.active) return false;

    // Search
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      const name = (rule.name || '').toLowerCase();
      const description = (rule.description || '').toLowerCase();
      const ruleId = (rule.id || '').toLowerCase();
      
      if (!name.includes(query) && !description.includes(query) && !ruleId.includes(query)) {
        return false;
      }
    }

    return true;
  });

  // Stats
  const stats = {
    total: rules.length,
    active: rules.filter(r => r.active !== false).length,
    inactive: rules.filter(r => r.active === false).length,
    ubuntu: rules.filter(r => r.os_type === 'ubuntu').length,
    windows: rules.filter(r => r.os_type === 'windows').length,
    bySeverity: {
      critical: rules.filter(r => r.severity?.toLowerCase() === 'critical').length,
      high: rules.filter(r => r.severity?.toLowerCase() === 'high').length,
      medium: rules.filter(r => r.severity?.toLowerCase() === 'medium').length,
      low: rules.filter(r => r.severity?.toLowerCase() === 'low').length,
    },
  };

  if (loading) {
    return (
      <div className="rules-page">
        <h1>📋 Rules</h1>
        <div className="loading">Loading rules...</div>
      </div>
    );
  }

  return (
    <div className="rules-page">
      {/* HEADER */}
      <div className="page-header">
        <h1>📋 CIS Benchmark Rules</h1>
        <button className="btn-primary" onClick={fetchRules}>
          🔄 Refresh
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {/* STATS */}
      <div className="rules-stats">
        <div className="stat-box">
          <div className="stat-value">{stats.total}</div>
          <div className="stat-label">Total Rules</div>
        </div>
        <div className="stat-box active">
          <div className="stat-value">{stats.active}</div>
          <div className="stat-label">Active</div>
        </div>
        <div className="stat-box inactive">
          <div className="stat-value">{stats.inactive}</div>
          <div className="stat-label">Inactive</div>
        </div>
        <div className="stat-box ubuntu">
          <div className="stat-value">🐧 {stats.ubuntu}</div>
          <div className="stat-label">Ubuntu</div>
        </div>
        <div className="stat-box windows">
          <div className="stat-value">🪟 {stats.windows}</div>
          <div className="stat-label">Windows</div>
        </div>
      </div>

      {/* FILTERS */}
      <div className="filters-bar">
        <div className="filter-group">
          <label>OS Type:</label>
          <select value={filterOS} onChange={(e) => setFilterOS(e.target.value)}>
            <option value="all">All ({rules.length})</option>
            <option value="ubuntu">Ubuntu ({stats.ubuntu})</option>
            <option value="windows">Windows ({stats.windows})</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Severity:</label>
          <select value={filterSeverity} onChange={(e) => setFilterSeverity(e.target.value)}>
            <option value="all">All</option>
            <option value="critical">Critical ({stats.bySeverity.critical})</option>
            <option value="high">High ({stats.bySeverity.high})</option>
            <option value="medium">Medium ({stats.bySeverity.medium})</option>
            <option value="low">Low ({stats.bySeverity.low})</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Category:</label>
          <select value={filterCategory} onChange={(e) => setFilterCategory(e.target.value)}>
            <option value="all">All Categories</option>
            {categories.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>Status:</label>
          <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
            <option value="all">All</option>
            <option value="active">Active ({stats.active})</option>
            <option value="inactive">Inactive ({stats.inactive})</option>
          </select>
        </div>

        <div className="filter-group search-group">
          <label>Search:</label>
          <input
            type="text"
            placeholder="Search rules..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* RULES GRID */}
      <div className="rules-grid">
        {filteredRules.length === 0 ? (
          <div className="empty-state">
            <p>😔 No rules found matching your criteria</p>
          </div>
        ) : (
          filteredRules.map((rule) => (
            <div
              key={rule.id}
              className={`rule-card ${rule.active === false ? 'inactive' : ''}`}
              onClick={() => setSelectedRule(rule)}
            >
              <div className="rule-card-header">
                <div className="rule-title-section">
                  <h3>{rule.name || rule.id}</h3>
                  <span className="rule-id">{rule.id}</span>
                </div>
                <div className="rule-badges">
                  <span
                    className="severity-badge"
                    style={{
                      background: `${getSeverityColor(rule.severity)}22`,
                      color: getSeverityColor(rule.severity),
                      border: `2px solid ${getSeverityColor(rule.severity)}`,
                    }}
                  >
                    {getSeverityIcon(rule.severity)} {(rule.severity || '').toUpperCase()}
                  </span>
                  <span className="os-badge">
                    {rule.os_type === 'ubuntu' ? '🐧 Ubuntu' : '🪟 Windows'}
                  </span>
                </div>
              </div>

              <div className="rule-card-body">
                <div className="rule-category">
                  📁 {rule.category || 'Uncategorized'}
                </div>
                <p className="rule-description">
                  {rule.description || 'No description available'}
                </p>
              </div>

              <div className="rule-card-footer">
                <span className={`status-indicator ${rule.active !== false ? 'active' : 'inactive'}`}>
                  {rule.active !== false ? '✅ Active' : '⏸️ Inactive'}
                </span>
                <button className="btn-view-details">View Details →</button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* RULE DETAILS MODAL */}
      {selectedRule && (
        <div className="modal-overlay" onClick={() => setSelectedRule(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>📋 Rule Details: {selectedRule.id}</h2>
              <button className="modal-close" onClick={() => setSelectedRule(null)}>
                ✕
              </button>
            </div>

            <div className="modal-body">
              <div className="detail-section">
                <h3>{selectedRule.name}</h3>
                <div className="rule-meta">
                  <span
                    className="severity-badge large"
                    style={{
                      background: `${getSeverityColor(selectedRule.severity)}22`,
                      color: getSeverityColor(selectedRule.severity),
                      border: `2px solid ${getSeverityColor(selectedRule.severity)}`,
                    }}
                  >
                    {getSeverityIcon(selectedRule.severity)} {(selectedRule.severity || '').toUpperCase()}
                  </span>
                  <span className="os-badge large">
                    {selectedRule.os_type === 'ubuntu' ? '🐧 Ubuntu' : '🪟 Windows'}
                  </span>
                  <span className="category-badge">
                    📁 {selectedRule.category}
                  </span>
                  <span className={`status-badge large ${selectedRule.active !== false ? 'active' : 'inactive'}`}>
                    {selectedRule.active !== false ? '✅ Active' : '⏸️ Inactive'}
                  </span>
                </div>
              </div>

              <div className="detail-section">
                <h3>Description</h3>
                <p>{selectedRule.description || 'No description available'}</p>
              </div>

              <div className="detail-section">
                <h3>Audit Command</h3>
                <pre className="code-block">{selectedRule.check_expression || 'N/A'}</pre>
              </div>

              <div className="detail-section">
                <h3>Remediation</h3>
                <p className="remediation-text">
                  {selectedRule.remediation || 'No remediation steps provided'}
                </p>
              </div>

              <div className="detail-section">
                <h3>Metadata</h3>
                <div className="detail-grid">
                  <div className="detail-item">
                    <span className="detail-label">Rule ID:</span>
                    <span className="detail-value">{selectedRule.id}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">OS Type:</span>
                    <span className="detail-value">{selectedRule.os_type}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Category:</span>
                    <span className="detail-value">{selectedRule.category}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Severity:</span>
                    <span className="detail-value">{selectedRule.severity}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Status:</span>
                    <span className="detail-value">
                      {selectedRule.active !== false ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn-secondary" onClick={() => setSelectedRule(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
