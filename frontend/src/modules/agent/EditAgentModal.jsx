import React, { useState } from 'react';
import { Edit, X } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useTheme } from '../../context/ThemeContext';
import '../violation/Modal.css';

export default function EditAgentModal({ agent, onClose, onSave }) {
  const { t } = useTranslation();
  const { theme } = useTheme();
  const [formData, setFormData] = useState({
    hostname: agent.hostname || '',
    ip_address: agent.ip_address || '',
    os: agent.os || '',
    version: agent.version || ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await onSave(agent.id, formData);
      onClose();
    } catch (error) {
      console.error('Failed to update agent:', error);
      alert('Failed to update agent');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`modal-overlay ${theme === 'light' ? 'light-mode' : ''}`} onClick={onClose}>
      <div className={`modal-content ${theme === 'light' ? 'light-mode' : ''}`} onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2><Edit size={24} /> {t('agents.editAgent')}</h2>
          <button className="modal-close" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <div className="form-group">
              <label>{t('agents.agentId')}:</label>
              <input type="text" value={agent.id} disabled />
            </div>

            <div className="form-group">
              <label>{t('agents.hostname')}: *</label>
              <input
                type="text"
                value={formData.hostname}
                onChange={(e) => setFormData({...formData, hostname: e.target.value})}
                required
                placeholder="server-01"
              />
            </div>

            <div className="form-group">
              <label>{t('agents.ipAddress')}:</label>
              <input
                type="text"
                value={formData.ip_address}
                onChange={(e) => setFormData({...formData, ip_address: e.target.value})}
                placeholder="192.168.1.100"
              />
            </div>

            <div className="form-group">
              <label>{t('agents.operatingSystem')}: *</label>
              <input
                type="text"
                value={formData.os}
                onChange={(e) => setFormData({...formData, os: e.target.value})}
                required
                placeholder="Ubuntu 22.04 LTS"
              />
            </div>

            <div className="form-group">
              <label>{t('agents.agentVersion')}:</label>
              <input
                type="text"
                value={formData.version}
                onChange={(e) => setFormData({...formData, version: e.target.value})}
                placeholder="1.0.0"
              />
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn-secondary" onClick={onClose}>
              {t('common.cancel')}
            </button>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? t('agents.saving') : t('agents.saveChanges')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
