import React, { useState } from 'react';
import { X } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useTheme } from '../../context/ThemeContext';
import '../violation/Modal.css';

export default function CreateRuleModal({ onClose, onCreate }) {
  const { t } = useTranslation();
  const { theme } = useTheme();
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    check_expression: '',
    severity: 'medium',
    category: 'Access Control',
    os_type: 'ubuntu',
    is_active: true
  });
  const [error, setError] = useState('');
  const [creating, setCreating] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.name.trim()) {
      setError('Rule name is required');
      return;
    }
    
    if (!formData.check_expression.trim()) {
      setError('Check expression is required');
      return;
    }

    setCreating(true);
    setError('');

    try {
      await onCreate(formData);
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create rule');
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className={`modal-overlay ${theme === 'light' ? 'light-mode' : ''}`} onClick={onClose}>
      <div className="modal-content modal-medium" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{t('rules.createRule')}</h2>
          <button className="modal-close" onClick={onClose}>
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            {error && <div className="error-message">{error}</div>}

            <div className="form-group">
              <label>{t('rules.ruleName')} *</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="e.g., SSH Root Login Disabled"
                required
              />
            </div>

            <div className="form-group">
              <label>{t('rules.description')}</label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                placeholder={t('rules.descriptionPlaceholder')}
                rows="3"
              />
            </div>

            <div className="form-group">
              <label>{t('rules.checkExpression')} *</label>
              <textarea
                name="check_expression"
                value={formData.check_expression}
                onChange={handleChange}
                placeholder="e.g., grep '^PermitRootLogin no' /etc/ssh/sshd_config"
                rows="3"
                required
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>{t('rules.severity')}</label>
                <select name="severity" value={formData.severity} onChange={handleChange}>
                  <option value="critical">{t('common.critical')}</option>
                  <option value="high">{t('common.high')}</option>
                  <option value="medium">{t('common.medium')}</option>
                  <option value="low">{t('common.low')}</option>
                </select>
              </div>

              <div className="form-group">
                <label>{t('rules.category')}</label>
                <select name="category" value={formData.category} onChange={handleChange}>
                  <option value="Access Control">{t('rules.accessControl')}</option>
                  <option value="Auditing">{t('rules.auditing')}</option>
                  <option value="Firewall">{t('rules.firewall')}</option>
                  <option value="System Updates">{t('rules.systemUpdates')}</option>
                  <option value="Password Policy">{t('rules.passwordPolicy')}</option>
                  <option value="Filesystem">{t('rules.fileSystem')}</option>
                  <option value="Logging">{t('rules.logging')}</option>
                  <option value="Network">{t('rules.network')}</option>
                  <option value="Antivirus">{t('rules.antivirus')}</option>
                  <option value="SSH">{t('rules.ssh')}</option>
                </select>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>{t('rules.osType')}</label>
                <select name="os_type" value={formData.os_type} onChange={handleChange}>
                  <option value="ubuntu">{t('rules.ubuntu')}</option>
                  <option value="windows">{t('rules.windows')}</option>
                </select>
              </div>

              <div className="form-group checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    name="is_active"
                    checked={formData.is_active}
                    onChange={handleChange}
                  />
                  <span>{t('common.active')}</span>
                </label>
              </div>
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn-secondary" onClick={onClose} disabled={creating}>
              {t('common.cancel')}
            </button>
            <button type="submit" className="btn-primary" disabled={creating}>
              {creating ? t('rules.creating') : t('rules.createRule')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
