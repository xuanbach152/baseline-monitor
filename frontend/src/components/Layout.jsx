import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Monitor,
    Home, 
  AlertTriangle, 
  FileText, 
  Settings, 
  Shield,
  ChevronLeft,
  ChevronRight,
  Sun,
  Moon
} from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import './Layout.css';

export default function Layout({ children }) {
  const location = useLocation();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const { theme, toggleTheme } = useTheme();

  const isActive = (path) => location.pathname === path;

  const navItems = [
    { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/agents', icon: Monitor, label: 'Agents' },
    { path: '/violations', icon: AlertTriangle, label: 'Violations' },
    { path: '/rules', icon: FileText, label: 'Rules' },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <div className={`layout-container ${theme === 'light' ? 'light-mode' : ''}`}>
      {/* SIDEBAR */}
      <aside className={`sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
        <div className="sidebar-header">
          <h1 className="sidebar-logo">
            <Shield size={16} />
            {!sidebarCollapsed && <span>Baseline Monitor</span>}
          </h1>
         <button
            className="sidebar-toggle"
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            title={sidebarCollapsed ? 'Expand' : 'Collapse'}
            >
            <Home size={20} color="#ff1744" strokeWidth={2.5} />
         </button>
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
            title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
            style={{
              background: theme === 'dark' ? '#f6f6f6ff' : '#040404ff',
              color: theme === 'dark' ? '#050505ff' : '#fefefeff',
            }}
          >
            {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
            {!sidebarCollapsed && <span>{theme === 'dark' ? 'Light' : 'Dark'} Mode</span>}
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
