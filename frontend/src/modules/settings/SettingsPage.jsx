import React, { useState } from 'react';
import { 
  Settings as SettingsIcon, 
  Save, 
  Search, 
  RefreshCw,
  Bell,
  Mail,
  MessageSquare,
  TrendingUp,
  Info,
  CheckCircle
} from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';
import './SettingsPage.css';

export default function SettingsPage() {
  const { theme } = useTheme();
  const [settings, setSettings] = useState({
    scanInterval: 3600,
    autoRefresh: true,
    refreshInterval: 30,
    notifications: {
      email: false,
      slack: false,
    },
    thresholds: {
      criticalCompliance: 50,
      warningCompliance: 70,
    },
  });

  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    // TODO: Save to backend or localStorage
    localStorage.setItem('app-settings', JSON.stringify(settings));
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className={`settings-page ${theme === 'light' ? 'light-mode' : ''}`}>
      <div className="page-header">
        <h1><SettingsIcon size={32} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 12 }} />Settings</h1>
        <button className="btn-primary" onClick={handleSave}>
          <Save size={16} /> Save Settings
        </button>
      </div>

      {saved && (
        <div className="success-message">
          <CheckCircle size={20} /> Settings saved successfully!
        </div>
      )}

      {/* SCAN SETTINGS */}
      <div className="settings-section">
        <h2><Search size={24} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 8 }} />Scan Configuration</h2>
        <div className="settings-grid">
          <div className="setting-item">
            <label htmlFor="scanInterval">
              Agent Scan Interval (seconds)
              <span className="setting-hint">How often agents should scan for violations</span>
            </label>
            <input
              id="scanInterval"
              type="number"
              min="60"
              max="86400"
              value={settings.scanInterval}
              onChange={(e) => setSettings({ ...settings, scanInterval: parseInt(e.target.value) })}
            />
          </div>
        </div>
      </div>

      {/* DASHBOARD SETTINGS */}
      <div className="settings-section">
        <h2><RefreshCw size={24} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 8 }} />Dashboard Configuration</h2>
        <div className="settings-grid">
          <div className="setting-item">
            <label>
              <input
                type="checkbox"
                checked={settings.autoRefresh}
                onChange={(e) => setSettings({ ...settings, autoRefresh: e.target.checked })}
              />
              Auto-refresh dashboard
            </label>
          </div>

          {settings.autoRefresh && (
            <div className="setting-item">
              <label htmlFor="refreshInterval">
                Refresh Interval (seconds)
                <span className="setting-hint">How often to refresh dashboard data</span>
              </label>
              <input
                id="refreshInterval"
                type="number"
                min="10"
                max="300"
                value={settings.refreshInterval}
                onChange={(e) => setSettings({ ...settings, refreshInterval: parseInt(e.target.value) })}
              />
            </div>
          )}
        </div>
      </div>

      {/* NOTIFICATION SETTINGS */}
      <div className="settings-section">
        <h2><Bell size={24} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 8 }} />Notifications</h2>
        <div className="settings-grid">
          <div className="setting-item">
            <label>
              <input
                type="checkbox"
                checked={settings.notifications.email}
                onChange={(e) => setSettings({
                  ...settings,
                  notifications: { ...settings.notifications, email: e.target.checked }
                })}
              />
              <Mail size={18} style={{ marginRight: 6 }} />
              Email Notifications
              <span className="setting-hint">Send email alerts for critical violations</span>
            </label>
          </div>

          <div className="setting-item">
            <label>
              <input
                type="checkbox"
                checked={settings.notifications.slack}
                onChange={(e) => setSettings({
                  ...settings,
                  notifications: { ...settings.notifications, slack: e.target.checked }
                })}
              />
              <MessageSquare size={18} style={{ marginRight: 6 }} />
              Slack Notifications
              <span className="setting-hint">Send Slack alerts for critical violations</span>
            </label>
          </div>
        </div>
      </div>

      {/* COMPLIANCE THRESHOLDS */}
      <div className="settings-section">
        <h2><TrendingUp size={24} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 8 }} />Compliance Thresholds</h2>
        <div className="settings-grid">
          <div className="setting-item">
            <label htmlFor="criticalThreshold">
              Critical Threshold (%)
              <span className="setting-hint">Compliance rate below this triggers critical alert</span>
            </label>
            <input
              id="criticalThreshold"
              type="number"
              min="0"
              max="100"
              value={settings.thresholds.criticalCompliance}
              onChange={(e) => setSettings({
                ...settings,
                thresholds: { ...settings.thresholds, criticalCompliance: parseInt(e.target.value) }
              })}
            />
          </div>

          <div className="setting-item">
            <label htmlFor="warningThreshold">
              Warning Threshold (%)
              <span className="setting-hint">Compliance rate below this triggers warning alert</span>
            </label>
            <input
              id="warningThreshold"
              type="number"
              min="0"
              max="100"
              value={settings.thresholds.warningCompliance}
              onChange={(e) => setSettings({
                ...settings,
                thresholds: { ...settings.thresholds, warningCompliance: parseInt(e.target.value) }
              })}
            />
          </div>
        </div>
      </div>

      {/* SYSTEM INFO */}
      <div className="settings-section">
        <h2><Info size={24} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 8 }} />System Information</h2>
        <div className="info-grid">
          <div className="info-item">
            <span className="info-label">Version:</span>
            <span className="info-value">1.0.0</span>
          </div>
          <div className="info-item">
            <span className="info-label">Backend API:</span>
            <span className="info-value">{import.meta.env.VITE_API_URL || 'http://localhost:8000'}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Build Date:</span>
            <span className="info-value">{new Date().toLocaleDateString()}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
