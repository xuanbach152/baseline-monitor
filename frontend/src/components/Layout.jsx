import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Monitor,
    Home, 
  AlertTriangle, 
  FileText, 
  Settings,
  FileBarChart,
  Sun,
  Moon
} from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useTheme } from '../context/ThemeContext';
import './Layout.css';

export default function Layout({ children }) {
  const { t } = useTranslation();
  const location = useLocation();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const { theme, toggleTheme } = useTheme();

  const isActive = (path) => location.pathname === path;

  const navItems = [
    { path: '/', icon: LayoutDashboard, label: t('nav.dashboard') },
    { path: '/agents', icon: Monitor, label: t('nav.agents') },
    { path: '/violations', icon: AlertTriangle, label: t('nav.violations') },
    { path: '/rules', icon: FileText, label: t('nav.rules') },
    { path: '/reports', icon: FileBarChart, label: t('nav.reports') },
    { path: '/settings', icon: Settings, label: t('nav.settings') },
  ];

  return (
    <div className={`layout-container ${theme === 'light' ? 'light-mode' : ''}`}>
      {/* SIDEBAR */}
      <aside className={`sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
        <div className="sidebar-header">
         <button
            className="sidebar-toggle"
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            title={sidebarCollapsed ? 'Expand' : 'Collapse'}
            > {theme === 'dark' ? <Home size={50} color="#050505ff" strokeWidth={2.5}/> : <Home size={50} color="#f3f1f1ff" strokeWidth={2.5} />}
         </button>
          <h1 className="sidebar-logo">
            {!sidebarCollapsed && <span>Baseline Monitor</span>}
          </h1>
        </div>

        <nav className="sidebar-nav">
          {navItems.map((item) => {
            const IconComponent = item.icon;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-item ${isActive(item.path) ? 'active' : ''}`}
                title={item.label}
              >
                <IconComponent size={20} className="nav-icon" />
                {!sidebarCollapsed && <span className="nav-label">{item.label}</span>}
              </Link>
            );
          })}
        </nav>

        <div className="sidebar-footer">
          <button
            className="theme-toggle"
            onClick={toggleTheme}
            title={theme === 'dark' ? t('common.lightMode') : t('common.darkMode')}
            style={{
              background: theme === 'dark' ? '#f6f6f6ff' : '#040404ff',
              color: theme === 'dark' ? '#050505ff' : '#fefefeff',
            }}
          >
            {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
            {!sidebarCollapsed && <span>{theme === 'dark' ? t('common.lightMode') : t('common.darkMode')}</span>}
          </button>
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <main className={`main-content ${sidebarCollapsed ? 'expanded' : ''}`}>
        <div className="content-wrapper">
          {children}
        </div>
      </main>
    </div>
  );
}
