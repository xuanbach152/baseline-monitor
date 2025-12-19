import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Settings as SettingsIcon, 
  Info,
  Globe
} from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useTheme } from '../../context/ThemeContext';
import './SettingsPage.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export default function SettingsPage() {
  const { theme } = useTheme();
  const { t, i18n } = useTranslation();
  const [language, setLanguage] = useState(i18n.language);

  const handleLanguageChange = (lang) => {
    setLanguage(lang);
    i18n.changeLanguage(lang);
    localStorage.setItem('language', lang);
  };

  return (
    <div className={`settings-page ${theme === 'light' ? 'light-mode' : ''}`}>
      <div className="page-header">
        <h1><SettingsIcon size={32} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 12 }} />{t('settings.title')}</h1>
      </div>

      {/* LANGUAGE SETTINGS */}
      <div className="settings-section">
        <h2><Globe size={24} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 8 }} />{t('settings.language')}</h2>
        <div className="settings-grid">
          <div className="setting-item">
            <label htmlFor="language">
              {t('settings.selectLanguage')}
              <span className="setting-hint">Choose your preferred language / Chọn ngôn ngữ ưa thích</span>
            </label>
            <select
              id="language"
              value={language}
              onChange={(e) => handleLanguageChange(e.target.value)}
              style={{ fontSize: '1rem', padding: '12px' }}
            >
              <option value="en"> {t('settings.english')}</option>
              <option value="vi"> {t('settings.vietnamese')}</option>
              <option value="ja"> {t('settings.japanese')}</option>
              <option value="th"> {t('settings.thai')}</option>
              <option value="fr"> {t('settings.french')}</option>
              <option value="zh"> {t('settings.chinese')}</option>
            </select>
          </div>
        </div>
      </div>

      {/* SYSTEM INFO */}
      <div className="settings-section">
        <h2><Info size={24} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 8 }} />{t('settings.systemInfo')}</h2>
        <div className="info-grid">
          <div className="info-item">
            <span className="info-label">{t('settings.version')}:</span>
            <span className="info-value">1.0.0</span>
          </div>
          <div className="info-item">
            <span className="info-label">{t('settings.backendApi')}:</span>
            <span className="info-value">{import.meta.env.VITE_API_URL || 'http://localhost:8000'}</span>
          </div>
          <div className="info-item">
            <span className="info-label">{t('settings.buildDate')}:</span>
            <span className="info-value">{new Date().toLocaleDateString()}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
