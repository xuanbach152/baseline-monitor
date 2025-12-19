import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  FileText, 
  RefreshCw, 
  Shield, 
  AlertTriangle,
  XCircle,
  Clock,
  Activity,
  CheckCircle,
  XOctagon,
  Server,
  Laptop,
  Eye,
  Folder,
  Edit,
  Trash2,
  Plus
} from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useTheme } from '../../context/ThemeContext';
import EditRuleModal from './EditRuleModal';
import CreateRuleModal from './CreateRuleModal';
import './RulesPage.css';

const API_URL = import.meta.env.VITE_API_URL;

export default function RulesPage() {
  const { t } = useTranslation();
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedRule, setSelectedRule] = useState(null);
  const [editModal, setEditModal] = useState(null);
  const [createModal, setCreateModal] = useState(false);
  const { theme } = useTheme();

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
    const iconProps = { size: 14, style: { display: 'inline', verticalAlign: 'middle' } };
    if (sev === 'critical') return <XCircle {...iconProps} />;
    if (sev === 'high') return <AlertTriangle {...iconProps} />;
    if (sev === 'medium') return <Clock {...iconProps} />;
    if (sev === 'low') return <Shield {...iconProps} />;
    return <Activity {...iconProps} />;
  };

  const handleEdit = async (ruleId, data) => {
    try {
      await axios.put(`${API_URL}/rules/${ruleId}`, data);
      await fetchRules();
      setEditModal(null);
    } catch (err) {
      console.error('Failed to update rule:', err);
      throw err;
    }
  };

  const handleCreate = async (data) => {
    try {
      await axios.post(`${API_URL}/rules`, data);
      await fetchRules();
      setCreateModal(false);
    } catch (err) {
      console.error('Failed to create rule:', err);
      throw err;
    }
  };

  const handleDelete = async (ruleId) => {
    if (!window.confirm('Are you sure you want to delete this rule? This action cannot be undone.')) {
      return;
    }
    
    try {
      await axios.delete(`${API_URL}/rules/${ruleId}`);
      await fetchRules();
      setSelectedRule(null);
    } catch (err) {
      console.error('Failed to delete rule:', err);
      alert('Failed to delete rule');
    }
  };

  const handleToggleActive = async (ruleId) => {
    try {
      await axios.patch(`${API_URL}/rules/${ruleId}/toggle`);
      await fetchRules();
    } catch (err) {
      console.error('Failed to toggle rule:', err);
      alert('Failed to toggle rule status');
    }
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
      <div className={`rules-page ${theme === 'light' ? 'light-mode' : ''}`}>
        <div className="page-header">
          <h1><FileText size={32} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 12 }} />CIS Rules</h1>
        </div>
        <div className="loading"><Activity size={24} /> Loading rules...</div>
      </div>
    );
  }

  return (
    <div className={`rules-page ${theme === 'light' ? 'light-mode' : ''}`}>
      {/* HEADER */}
        <div className="page-header">
              <h1 className="page-title">
                <FileText size={32} /> {t('rules.title')}
              </h1>

        <div className="page-actions">
          <button className="btn-primary" onClick={() => setCreateModal(true)}>
            <Plus size={16} />
            {t('rules.addRule')}
          </button>

          <button className="btn-primary" onClick={fetchRules}>
            <RefreshCw size={16} />
            {t('rules.refresh')}
          </button>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      {/* STATS */}
      <div className="rules-stats">
        <div className="stat-box">
          <div className="stat-value">{stats.total}</div>
          <div className="stat-label">{t('rules.totalRules')}</div>
        </div>
        <div className="stat-box active">
          <div className="stat-value">{stats.active}</div>
          <div className="stat-label">{t('rules.active')}</div>
        </div>
        <div className="stat-box inactive">
          <div className="stat-value">{stats.inactive}</div>
          <div className="stat-label">{t('rules.inactive')}</div>
        </div>
        <div className="stat-box ubuntu">
          <div className="stat-value"><Server size={20} /> {stats.ubuntu}</div>
          <div className="stat-label">{t('rules.ubuntu')}</div>
        </div>
        <div className="stat-box windows">
          <div className="stat-value"><Laptop size={20} /> {stats.windows}</div>
          <div className="stat-label">{t('rules.windows')}</div>
        </div>
      </div>

      {/* FILTERS */}
      <div className="filters-bar">
        <div className="filter-group">
          <label>{t('rules.osType')}:</label>
          <select value={filterOS} onChange={(e) => setFilterOS(e.target.value)}>
            <option value="all">{t('rules.all')} ({rules.length})</option>
            <option value="ubuntu">{t('rules.ubuntu')} ({stats.ubuntu})</option>
            <option value="windows">{t('rules.windows')} ({stats.windows})</option>
          </select>
        </div>

        <div className="filter-group">
          <label>{t('rules.severity')}:</label>
          <select value={filterSeverity} onChange={(e) => setFilterSeverity(e.target.value)}>
            <option value="all">{t('rules.all')}</option>
            <option value="critical">{t('common.critical')} ({stats.bySeverity.critical})</option>
            <option value="high">{t('common.high')} ({stats.bySeverity.high})</option>
            <option value="medium">{t('common.medium')} ({stats.bySeverity.medium})</option>
            <option value="low">{t('common.low')} ({stats.bySeverity.low})</option>
          </select>
        </div>

        <div className="filter-group">
          <label>{t('rules.category')}:</label>
          <select value={filterCategory} onChange={(e) => setFilterCategory(e.target.value)}>
            <option value="all">{t('rules.allCategories')}</option>
            {categories.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>{t('rules.status')}:</label>
          <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
            <option value="all">{t('rules.all')}</option>
            <option value="active">{t('rules.active')} ({stats.active})</option>
            <option value="inactive">{t('rules.inactive')} ({stats.inactive})</option>
          </select>
        </div>

        <div className="filter-group search-group">
          <label>{t('common.search')}:</label>
          <input
            type="text"
            placeholder={t('rules.searchRules')}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* RULES GRID */}
      <div className="rules-grid">
        {filteredRules.length === 0 ? (
          <div className="empty-state">
            <p>{t('rules.noRules')}</p>
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
                    {rule.os_type === 'ubuntu' ? <><Server size={14} /> Ubuntu</> : <><Laptop size={14} /> Windows</>}
                  </span>
                </div>
              </div>

              <div className="rule-card-body">
                <div className="rule-category">
                  <Shield size={16} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 6 }} />
                  {rule.category || 'Uncategorized'}
                </div>
                <p className="rule-description">
                  {rule.description || 'No description available'}
                </p>
              </div>

              <div className="rule-card-footer">
                <span className={`status-indicator ${rule.active !== false ? 'active' : 'inactive'}`}>
                  {rule.active !== false ? <><CheckCircle size={14} /> Active</> : <><XOctagon size={14} /> Inactive</>}
                </span>
                <div className="rule-actions">
                  <button
                    className="action-btn toggle-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleToggleActive(rule.id);
                    }}
                    title={rule.active !== false ? 'Deactivate' : 'Activate'}
                  >
                    {rule.active !== false ? <XOctagon size={16} /> : <CheckCircle size={16} />}
                  </button>
                  <button
                    className="action-btn edit-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      setEditModal(rule);
                    }}
                    title="Edit Rule"
                  >
                    <Edit size={16} />
                  </button>
                  <button
                    className="action-btn delete-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(rule.id);
                    }}
                    title="Delete Rule"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
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
              <h2><FileText size={24} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 8 }} />Rule Details: {selectedRule.id}</h2>
              <button className="modal-close" onClick={() => setSelectedRule(null)}>
                <XOctagon size={24} />
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
                    {selectedRule.os_type === 'ubuntu' ? <><Server size={14} /> Ubuntu</> : <><Laptop size={14} /> Windows</>}
                  </span>
                  <span className="category-badge">
                    <Folder size={14} /> {selectedRule.category}
                  </span>
                  <span className={`status-badge large ${selectedRule.active !== false ? 'active' : 'inactive'}`}>
                    {selectedRule.active !== false ? <><CheckCircle size={14} /> Active</> : <><XOctagon size={14} /> Inactive</>}
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

      {/* EDIT RULE MODAL */}
      {editModal && (
        <EditRuleModal
          rule={editModal}
          onClose={() => setEditModal(null)}
          onSave={handleEdit}
        />
      )}

      {/* CREATE RULE MODAL */}
      {createModal && (
        <CreateRuleModal
          onClose={() => setCreateModal(false)}
          onCreate={handleCreate}
        />
      )}
    </div>
  );
}
