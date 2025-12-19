import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Monitor, 
  RefreshCw, 
  Server, 
  Laptop, 
  Clock, 
  Wifi, 
  WifiOff,
  X,
  FileText,
  Activity,
  HardDrive,
  Edit,
  Trash2
} from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useTheme } from '../../context/ThemeContext';
import EditAgentModal from './EditAgentModal';
import './AgentsPage.css';

const API_URL = import.meta.env.VITE_API_URL;

export default function AgentsPage() {
  const { t } = useTranslation();
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterStatus, setFilterStatus] = useState('all'); // all, online, offline
  const [filterOS, setFilterOS] = useState('all'); // all, ubuntu, windows
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [editModal, setEditModal] = useState(null);
  const { theme } = useTheme();

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(`${API_URL}/agents?limit=1000`);
      setAgents(res.data || []);
    } catch (err) {
      setError('Failed to load agents');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchAgentDetails = async (agentId) => {
    try {
      const res = await axios.get(`${API_URL}/agents/${agentId}`);
      setSelectedAgent(res.data);
    } catch (err) {
      console.error('Failed to fetch agent details:', err);
    }
  };

  const filteredAgents = agents.filter((agent) => {
    // Filter by status
    if (filterStatus === 'online' && !agent.is_online) return false;
    if (filterStatus === 'offline' && agent.is_online) return false;

    // Filter by OS
    if (filterOS !== 'all' && agent.os_type !== filterOS) return false;

    // Search by hostname or IP
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      const hostname = (agent.hostname || '').toLowerCase();
      const ip = (agent.ip_address || '').toLowerCase();
      if (!hostname.includes(query) && !ip.includes(query)) return false;
    }

    return true;
  });

  const getComplianceColor = (rate) => {
    if (rate >= 80) return '#4fd1c5';
    if (rate >= 50) return '#ffd600';
    return '#ff1744';
  };

  const getStatusBadge = (isOnline) => (
    <span className={`status-badge ${isOnline ? 'online' : 'offline'}`}>
      {isOnline ? <><Wifi size={14} /> Online</> : <><WifiOff size={14} /> Offline</>}
    </span>
  );

  const handleEdit = async (agentId, data) => {
    try {
      await axios.put(`${API_URL}/agents/${agentId}`, data);
      await fetchAgents(); // Refresh list
      setEditModal(null);
    } catch (err) {
      console.error('Failed to update agent:', err);
      throw err;
    }
  };

  const handleDelete = async (agentId) => {
    if (!window.confirm('Are you sure you want to delete this agent? This will also delete all its violations.')) {
      return;
    }
    
    try {
      await axios.delete(`${API_URL}/agents/${agentId}`);
      await fetchAgents(); // Refresh list
      setSelectedAgent(null);
    } catch (err) {
      console.error('Failed to delete agent:', err);
      alert('Failed to delete agent');
    }
  };

  if (loading) {
    return (
      <div className={`agents-page ${theme === 'light' ? 'light-mode' : ''}`}>
        <div className="page-header">
          <h1><Monitor size={32} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 12 }} />Agents</h1>
        </div>
        <div className="loading"><Activity size={24} /> Loading agents...</div>
      </div>
    );
  }

  return (
    <div className={`agents-page ${theme === 'light' ? 'light-mode' : ''}`}>
      {/* HEADER */}
      <div className="page-header">
        <h1><Monitor size={32} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 12 }} />{t('agents.title')}</h1>
        <button className="btn-primary" onClick={fetchAgents}>
          <RefreshCw size={16} /> {t('agents.refresh')}
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {/* FILTERS */}
      <div className="filters-bar">
        <div className="filter-group">
          <label>{t('agents.status')}:</label>
          <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
            <option value="all">{t('rules.all')} ({agents.length})</option>
            <option value="online">{t('agents.online')} ({agents.filter(a => a.is_online).length})</option>
            <option value="offline">{t('agents.offline')} ({agents.filter(a => !a.is_online).length})</option>
          </select>
        </div>

        <div className="filter-group">
          <label>{t('agents.os')}:</label>
          <select value={filterOS} onChange={(e) => setFilterOS(e.target.value)}>
            <option value="all">{t('agents.allOS')}</option>
            <option value="ubuntu">{t('rules.ubuntu')}</option>
            <option value="windows">{t('rules.windows')}</option>
          </select>
        </div>

        <div className="filter-group search-group">
          <label>{t('common.search')}:</label>
          <input
            type="text"
            placeholder={t('agents.searchAgents')}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* STATS SUMMARY */}
      <div className="agents-stats">
        <div className="stat-box total">
          <div className="stat-value">{agents.length}</div>
          <div className="stat-label">{t('agents.total')}</div>
        </div>
        <div className="stat-box online">
          <div className="stat-value">{agents.filter(a => a.is_online).length}</div>
          <div className="stat-label">{t('agents.online')}</div>
        </div>
        <div className="stat-box offline">
          <div className="stat-value">{agents.filter(a => !a.is_online).length}</div>
          <div className="stat-label">{t('agents.offline')}</div>
        </div>
        <div className="stat-box avg">
          <div className="stat-value">
            {agents.length > 0
              ? ((agents.reduce((sum, a) => sum + (a.compliance_rate || 0), 0) / agents.length).toFixed(1))
              : 0}%
          </div>
          <div className="stat-label">{t('agents.compliance')}</div>
        </div>
      </div>

      {/* AGENTS GRID */}
      <div className="agents-grid">
        {filteredAgents.length === 0 ? (
          <div className="empty-state">
            <Monitor size={48} style={{ opacity: 0.3, marginBottom: 16 }} />
            <p>{t('agents.noAgents')}</p>
          </div>
        ) : (
          filteredAgents.map((agent) => (
            <div
              key={agent.id}
              className="agent-card"
              onClick={() => fetchAgentDetails(agent.id)}
            >
              <div className="agent-card-header">
                <h3>{agent.hostname || 'Unknown'}</h3>
                {getStatusBadge(agent.is_online)}
              </div>

              <div className="agent-card-body">
                <div className="agent-info">
                  <span className="info-label"><HardDrive size={14} /> OS:</span>
                  <span className="info-value">
                    {agent.os_type === 'ubuntu' ? <><Server size={14} /> Ubuntu</> : <><Laptop size={14} /> Windows</>} {agent.os_version || ''}
                  </span>
                </div>

                <div className="agent-info">
                  <span className="info-label">IP:</span>
                  <span className="info-value">{agent.ip_address || 'N/A'}</span>
                </div>

                <div className="agent-info">
                  <span className="info-label"><Clock size={14} /> Last Seen:</span>
                  <span className="info-value">
                    {agent.last_heartbeat
                      ? new Date(agent.last_heartbeat).toLocaleString()
                      : 'Never'}
                  </span>
                </div>

                <div className="agent-info">
                  <span className="info-label"><Activity size={14} /> Last Scan:</span>
                  <span className="info-value">
                    {agent.last_scan_at
                      ? new Date(agent.last_scan_at).toLocaleString()
                      : 'Never'}
                  </span>
                </div>
              </div>

              <div className="agent-card-footer">
                <div className="compliance-bar">
                  <div className="compliance-label">
                    Compliance: <strong>{agent.compliance_rate || 0}%</strong>
                  </div>
                  <div className="compliance-progress">
                    <div
                      className="compliance-fill"
                      style={{
                        width: `${agent.compliance_rate || 0}%`,
                        background: getComplianceColor(agent.compliance_rate || 0),
                      }}
                    />
                  </div>
                </div>
                <div className="agent-actions">
                  <button
                    className="action-btn edit-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      setEditModal(agent);
                    }}
                    title="Edit Agent"
                  >
                    <Edit size={16} />
                  </button>
                  <button
                    className="action-btn delete-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(agent.id);
                    }}
                    title="Delete Agent"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* AGENT DETAILS MODAL */}
      {selectedAgent && (
        <div className="modal-overlay" onClick={() => setSelectedAgent(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2><FileText size={24} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 8 }} />Agent Details: {selectedAgent.hostname}</h2>
              <button className="modal-close" onClick={() => setSelectedAgent(null)}>
                <X size={24} />
              </button>
            </div>

            <div className="modal-body">
              <div className="detail-section">
                <h3>System Information</h3>
                <div className="detail-grid">
                  <div className="detail-item">
                    <span className="detail-label">Hostname:</span>
                    <span className="detail-value">{selectedAgent.hostname}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">IP Address:</span>
                    <span className="detail-value">{selectedAgent.ip_address}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">MAC Address:</span>
                    <span className="detail-value">{selectedAgent.mac_address || 'N/A'}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">OS Type:</span>
                    <span className="detail-value">{selectedAgent.os_type}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">OS Version:</span>
                    <span className="detail-value">{selectedAgent.os_version}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Status:</span>
                    {getStatusBadge(selectedAgent.is_online)}
                  </div>
                </div>
              </div>

              <div className="detail-section">
                <h3>Activity</h3>
                <div className="detail-grid">
                  <div className="detail-item">
                    <span className="detail-label">Registered At:</span>
                    <span className="detail-value">
                      {new Date(selectedAgent.created_at).toLocaleString()}
                    </span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Last Heartbeat:</span>
                    <span className="detail-value">
                      {new Date(selectedAgent.last_heartbeat).toLocaleString()}
                    </span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Last Scan:</span>
                    <span className="detail-value">
                      {selectedAgent.last_scan_at
                        ? new Date(selectedAgent.last_scan_at).toLocaleString()
                        : 'Never'}
                    </span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Compliance Rate:</span>
                    <span
                      className="detail-value"
                      style={{ color: getComplianceColor(selectedAgent.compliance_rate || 0) }}
                    >
                      <strong>{selectedAgent.compliance_rate || 0}%</strong>
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn-secondary" onClick={() => setSelectedAgent(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* EDIT AGENT MODAL */}
      {editModal && (
        <EditAgentModal
          agent={editModal}
          onClose={() => setEditModal(null)}
          onSave={handleEdit}
        />
      )}
    </div>
  );
}
