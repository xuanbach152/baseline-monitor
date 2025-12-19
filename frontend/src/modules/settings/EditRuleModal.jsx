import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';
import '../violation/Modal.css';

export default function EditRuleModal({ rule, onClose, onSave }) {
  const { theme } = useTheme();
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    check_expression: '',
    severity: 'medium',
    category: 'security',
    os_type: 'ubuntu',
    is_active: true
  });
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (rule) {
      setFormData({
        name: rule.name || '',
        description: rule.description || '',
        check_expression: rule.check_expression || '',
        severity: rule.severity || 'medium',
        category: rule.category || 'security',
        os_type: rule.os_type || 'ubuntu',
        is_active: rule.is_active !== undefined ? rule.is_active : true
      });
    }
  }, [rule]);

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

    setSaving(true);
    setError('');

    try {
      await onSave(rule.id, formData);
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update rule');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className={`modal-overlay ${theme === 'light' ? 'light-mode' : ''}`} onClick={onClose}>
      <div className="modal-content modal-medium" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Edit Rule</h2>
          <button className="modal-close" onClick={onClose}>
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            {error && <div className="error-message">{error}</div>}

            <div className="form-group">
              <label>Rule Name *</label>
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
              <label>Description</label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                placeholder="Describe what this rule checks..."
                rows="3"
              />
            </div>

            <div className="form-group">
              <label>Check Expression *</label>
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
                <label>Severity</label>
                <select name="severity" value={formData.severity} onChange={handleChange}>
                  <option value="critical">Critical</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              </div>

              <div className="form-group">
                <label>Category</label>
                <select name="category" value={formData.category} onChange={handleChange}>
                  <option value="security">Security</option>
                  <option value="compliance">Compliance</option>
                  <option value="configuration">Configuration</option>
                  <option value="performance">Performance</option>
                </select>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>OS Type</label>
                <select name="os_type" value={formData.os_type} onChange={handleChange}>
                  <option value="ubuntu">Ubuntu</option>
                  <option value="windows">Windows</option>
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
                  <span>Active</span>
                </label>
              </div>
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn-secondary" onClick={onClose} disabled={saving}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={saving}>
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
