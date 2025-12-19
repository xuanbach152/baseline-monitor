import React, { useState } from 'react';
import { CheckCircle, X } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useTheme } from '../../context/ThemeContext';
import './Modal.css';

export default function ResolveModal({ violation, onClose, onResolve }) {
  const { t } = useTranslation();
  const { theme } = useTheme();
  const [notes, setNotes] = useState('');
  const [resolvedBy, setResolvedBy] = useState('admin'); 
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await onResolve(violation.id, {
        resolved_at: new Date().toISOString(),
        resolved_by: resolvedBy,
        resolution_notes: notes
      });
      onClose();
    } catch (error) {
      console.error('Failed to resolve:', error);
      alert('Failed to resolve violation');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`modal-overlay ${theme === 'light' ? 'light-mode' : ''}`} onClick={onClose}>
      <div className={`modal-content ${theme === 'light' ? 'light-mode' : ''}`} onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2><CheckCircle size={24} /> {t('violations.resolveViolation')}</h2>
          <button className="modal-close" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <div className="form-group">
              <label>{t('violations.violationId')}:</label>
              <input type="text" value={violation.id} disabled />
            </div>

            <div className="form-group">
              <label>{t('violations.message')}:</label>
              <input type="text" value={violation.message} disabled />
            </div>

            <div className="form-group">
              <label>{t('violations.resolvedBy')}:</label>
              <input
                type="text"
                value={resolvedBy}
                onChange={(e) => setResolvedBy(e.target.value)}
                required
                placeholder={t('violations.enterName')}
              />
            </div>

            <div className="form-group">
              <label>{t('violations.resolutionNotes')}:</label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                required
                placeholder={t('violations.describeResolution')}
                rows={4}
              />
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn-secondary" onClick={onClose}>
              {t('common.cancel')}
            </button>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? t('violations.resolving') : t('violations.markResolved')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
