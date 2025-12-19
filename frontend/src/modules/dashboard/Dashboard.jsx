
import React, { useEffect, useState } from "react";
import "./Dashboard.css";
import axios from "axios";
import { useTranslation } from 'react-i18next';
import { 
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, 
  CartesianGrid, PieChart, Pie, Cell, Legend, BarChart, Bar 
} from "recharts";
import { 
  Monitor, 
  AlertTriangle, 
  FileText, 
  TrendingUp,
  RefreshCw,
  Sun,
  Moon,
  Activity,
  Wifi
} from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';
import { useWebSocket } from '../../hooks/useWebSocket';
import Toast from '../../components/Toast';

const API_URL = import.meta.env.VITE_API_URL;

const StatCard = ({ title, value, subvalue, IconComponent, color }) => (
  <div className="stat-card" style={{ borderColor: color }}>
    <div className="stat-icon" style={{ color }}>
      <IconComponent size={32} />
    </div>
    <div className="stat-title">{title}</div>
    <div className="stat-value">{value}</div>
    {subvalue && <div className="stat-subvalue">{subvalue}</div>}
  </div>
);
 

export default function Dashboard() {
  const { t } = useTranslation();
  const [agentStats, setAgentStats] = useState({ total: 0, online: 0, offline: 0 });
  const [violationStats, setViolationStats] = useState({ total: 0, by_severity: {}, trend: [], top_5_agents: [] });
  const [ruleStats, setRuleStats] = useState({ total: 0, active: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const { theme } = useTheme();
  const [recentViolations, setRecentViolations] = useState([]);
  const [agentList, setAgentList] = useState([]);
  const [toastMessage, setToastMessage] = useState(null);
  
  // Fetch agents
  const fetchAgents = async () => {
    try {
      const res = await axios.get(`${API_URL}/agents?limit=1000`);
      setAgentList(res.data || []);
    } catch (err) {
      setAgentList([]);
    }
  };
  
  // Fetch recent violations
  const fetchRecentViolations = async () => {
    try {
      const res = await axios.get(`${API_URL}/violations/recent?limit=5&hours=168`);
      setRecentViolations(res.data || []);
    } catch (err) {
      setRecentViolations([]);
    }
  };
  
  // WebSocket connection with real-time updates
  const { isConnected } = useWebSocket({
    onViolationCreated: (data) => {
      // Refresh stats when new violation is created
      fetchAllStats();
      fetchRecentViolations();
      
      // Show toast notification for critical violations
      if (data.confidence_score && data.confidence_score > 0.8) {
        setToastMessage({
          message: `Critical violation detected: ${data.message || 'New security issue'}`,
          type: 'error'
        });
      }
    },
    onViolationResolved: () => {
      // Refresh stats when violation is resolved
      fetchAllStats();
      fetchRecentViolations();
    },
    onViolationDeleted: () => {
      // Refresh stats when violation is deleted
      fetchAllStats();
      fetchRecentViolations();
    },
    onAgentUpdated: () => {
      // Refresh agent stats
      fetchAgents();
      fetchAllStats();
    },
    onAgentDeleted: () => {
      // Refresh agent stats
      fetchAgents();
      fetchAllStats();
    }
  });
  
  useEffect(() => {
    fetchAgents();
  }, []);
      
  useEffect(() => {
    fetchRecentViolations();
  }, []);

  // Fetch all dashboard data
  const fetchAllStats = async () => {
    setLoading(true);
    setError(null);
    try {
      // Agents
      const agentRes = await axios.get(`${API_URL}/agents/stats`);
      setAgentStats(agentRes.data);

      // Violations
      const vioRes = await axios.get(`${API_URL}/violations/stats`);
      setViolationStats({
        total: vioRes.data.total_violations || 0,
        by_severity: vioRes.data.by_severity || {},
        trend: vioRes.data.trend || [],
        top_5_agents: vioRes.data.top_5_agents || [],
      });

      // Rules
      const ruleRes = await axios.get(`${API_URL}/rules`);
      const rules = ruleRes.data || [];
      setRuleStats({
        total: rules.length,
        active: rules.filter(r => r.active !== false).length,
      });
      setLastUpdated(new Date());
    } catch (err) {
      setError("Không thể tải dữ liệu dashboard");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAllStats();
  }, []);

  if (loading) return <div className="dashboard-container">Loading...</div>;

  return (
    <div className={`dashboard-container${theme === 'light' ? ' light-mode' : ''}`}>
      {/* HEADER */}
      <div style={{
        display: 'flex', justifyContent: 'flex-start', alignItems: 'center',
        width: '100%', margin: '0', padding: '20px 24px',
        borderBottom: '2.5px solid #31343a', minHeight: 80, marginBottom: 24
      }}>
        <h2 style={{ color: theme === 'light' ? '#23272b' : '#fdfdfdff', fontSize: '2rem', letterSpacing: 1, fontWeight: 800, textTransform: 'uppercase', margin: 0 }}>
          <Activity style={{ display: 'inline', marginRight: 8, color: theme === 'light' ? '#e80c26ff' : '#0cbb69ff', verticalAlign: 'middle' }} size={32} />
          {t('dashboard.title')}
        </h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          {/* WebSocket Connection Indicator */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            padding: '6px 12px',
            borderRadius: '20px',
            background: isConnected 
              ? 'rgba(79, 209, 197, 0.15)' 
              : 'rgba(176, 179, 184, 0.15)',
            border: `2px solid ${isConnected ? '#4fd1c5' : '#b0b3b8'}`,
            fontSize: '0.85rem',
            fontWeight: 600,
            color: isConnected ? '#4fd1c5' : '#b0b3b8'
          }}>
            <Wifi size={14} />
            {isConnected ? 'Live' : 'Offline'}
          </div>
          
          <button className="btn-primary" onClick={fetchAllStats}>
            <RefreshCw size={16} /> {t('common.refresh')}
          </button>
          {lastUpdated && (
            <span style={{ 
              color: theme === 'light' ? '#5a5a5a' : '#bfc7d5', 
              fontSize: '0.8rem', 
              fontWeight: 500,
              display: 'flex',
              alignItems: 'center',
              gap: 6
            }}>
              {t('dashboard.lastUpdated')}: {lastUpdated.toLocaleString('en-GB', { 
                day: '2-digit', 
                month: '2-digit', 
                year: 'numeric', 
                hour: '2-digit', 
                minute: '2-digit',
                second: '2-digit'
              })}
            </span>
          )}
        </div>
      </div>
      {error && <div className="error-msg">{error}</div>}

      {/* MAIN GRID: Custom layout for requested positions */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gridTemplateRows: 'auto auto auto auto',
        gridTemplateAreas: `
          'statcards piechart'
          'statcards agentstatus'
          'trendchart agentstatus'
          'top5chart barandtable'
        `,
        rowGap: '24px',
        columnGap: '24px',
        margin: '0',
        padding: '0 24px 24px 24px',
        alignItems: 'stretch',
      }}>
        {/* Stat cards: top left */}
        <div style={{ gridArea: 'statcards', display: 'flex', flexDirection: 'row', gap: 12, alignItems: 'flex-start' }}>
          <StatCard
            title={t('agents.title')}
            value={loading ? "..." : agentStats.total}
            subvalue={loading ? "" : `${t('agents.online')}: ${agentStats.online} | ${t('agents.offline')}: ${agentStats.offline}`}
            IconComponent={Monitor}
            color="#4fd1c5"
            style={{ minWidth: 145, minHeight: 150, padding: '0px 0px 0px 0px', fontSize: '1rem' }}
          />
          <StatCard
            title={t('violations.title')}
            value={loading ? "..." : violationStats.total}
            subvalue={
              loading
                ? ""
                : Object.entries(violationStats.by_severity).length > 0
                  ? Object.entries(violationStats.by_severity)
                      .map(([sev, cnt]) => `${sev}: ${cnt}`)
                      .join(" | ")
                  : ""
            }
            IconComponent={AlertTriangle}
            color="#f56565"
            style={{ minWidth: 145, minHeight: 150, padding: '0px 0px 0px 0px', fontSize: '1rem' }}
          />
          <StatCard
            title={t('rules.title')}
            value={loading ? "..." : ruleStats.total}
            subvalue={loading ? "" : `${t('dashboard.activeRules')}: ${ruleStats.active}`}
            IconComponent={FileText}
            color="#63b3ed"
            style={{ minWidth: 145, minHeight: 150, padding: '0px 0px 0px 0px', fontSize: '1rem' }}
          />
        </div>
        {/* Pie chart: top right */}
        <div style={{ gridArea: 'piechart', minWidth: 300,maxWidth: 600, minHeight: 260, display: 'flex', flexDirection: 'column', justifyContent: 'flex-start' }}>
          <div className="chart-container" style={{ borderRadius: 18, padding: 24, boxShadow: '0 2px 16px #ffd60033', border: '2px solid #ffd600', background: theme === 'light' ? '#fff' : '#23272b', width: '100%' }}>
            <h3 style={{ color: theme === 'light' ? '#23272b' : '#fff', marginBottom: 16, fontWeight: 700, fontSize: "1.12rem", letterSpacing: 0.5 }}>{t('violations.title')} - {t('violations.severity')}</h3>
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={Object.entries(violationStats.by_severity || {}).map(([key, value]) => ({ name: key, value }))}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={90}
                  innerRadius={48}
                  label={({ name, value }) => value > 0 ? `${name}: ${value}` : ''}
                  isAnimationActive={true}
                >
                  {['critical', 'high', 'medium', 'low'].map((sev, idx) => (
                    <Cell key={sev} fill={['#ff1744', '#ffd600', '#4fd1c5', '#63b3ed'][idx]} />
                  ))}
                </Pie>
                <Legend iconType="circle" verticalAlign="bottom" height={38} formatter={v => v.charAt(0).toUpperCase() + v.slice(1)} />
                <Tooltip contentStyle={{ background: theme === 'light' ? '#fff' : '#fdfeffff', border: '1px solid #31343a', color: theme === 'light' ? '#23272b' : '#fff' }} />
              </PieChart>
            </ResponsiveContainer>
            {(!violationStats.by_severity || Object.values(violationStats.by_severity).every(v => v === 0)) && (
              <div style={{ color: theme === 'light' ? '#23272b' : '#bfc7d5', textAlign: 'center', marginTop: 8, fontSize: '1.02rem' }}>
                Không có dữ liệu để hiển thị biểu đồ.
              </div>
            )}
          </div>
        </div>
        {/* Agent status: below pie chart */}
        <div style={{ gridArea: 'agentstatus', minWidth: 200,maxWidth: 380, minHeight: 200 }}>
          <div className="agent-status-list" style={{ borderRadius: 18, padding: 18, boxShadow: '0 2px 16px #31343a22', border: '2px solid #31343a', background: theme === 'light' ? '#fff' : '#23272b', minHeight: 100 }}>
            <h3 style={{ color: theme === 'light' ? '#23272b' : '#fff', marginBottom: 12, fontWeight: 700, fontSize: "1.08rem", letterSpacing: 0.5 }}>{t('agents.status')}</h3>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
              {agentList.length === 0 ? (
                <li style={{ color: theme === 'light' ? '#23272b' : '#bfc7d5', textAlign: 'center', padding: 12 }}>{t('agents.noAgents')}</li>
              ) : agentList.map(agent => (
                <li key={agent.id} style={{ display: 'flex', alignItems: 'center', marginBottom: 0 }}>
                  <span style={{
                    display: 'inline-block',
                    width: 14,
                    height: 14,
                    borderRadius: '50%',
                    background: agent.is_online ? '#4fd1c5' : '#ff1744',
                    marginRight: 10,
                    border: '2px solid #181b20',
                    boxShadow: agent.is_online ? '0 0 8px #4fd1c5aa' : '0 0 8px #ff1744aa'
                  }} />
                  <span style={{ color: theme === 'light' ? '#23272b' : '#fff', fontWeight: 500 }}>{agent.hostname && agent.hostname.length > 18 ? agent.hostname.slice(0, 15) + '...' : agent.hostname}</span>
                  <span style={{ color: agent.is_online ? '#4fd1c5' : '#ff1744', marginLeft: 'auto', fontWeight: 700, fontSize: '0.98em', textShadow: agent.is_online ? '0 0 6px #4fd1c555' : '0 0 6px #ff174455' }}>{agent.is_online ? t('agents.online') : t('agents.offline')}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
        {/* Line chart: below stat cards */}
        <div style={{ gridArea: 'trendchart', minWidth: 320,maxWidth:750, minHeight: 150,marginTop: -360 }}>
          <div className="chart-container" style={{ borderRadius: 18, padding: 18, boxShadow: '0 2px 16px #ff174422', border: '2px solid #ff1744', background: theme === 'light' ? '#fff' : '#23272b' }}>
            <h3 style={{ color: theme === 'light' ? '#23272b' : '#fff', marginBottom: 12, fontWeight: 700, fontSize: "1.08rem", letterSpacing: 0.5 }}>{t('dashboard.complianceTrend')}</h3>
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={violationStats.trend && violationStats.trend.length > 0 ? violationStats.trend : [{ date: '', count: 0 }]}
                margin={{ top: 8, right: 24, left: 0, bottom: 8 }}>
                <CartesianGrid stroke="#31343a" strokeDasharray="3 3" />
                <XAxis dataKey="date" stroke="#bfc7d5" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#bfc7d5" fontSize={12} tickLine={false} axisLine={false} allowDecimals={false} />
                <Tooltip 
                  contentStyle={{ background: theme === 'light' ? '#fff' : '#23272b', border: '1px solid #31343a', color: theme === 'light' ? '#23272b' : '#fff' }} 
                />
                <Line type="monotone" dataKey="count" stroke="#f56565" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
              </LineChart>
            </ResponsiveContainer>
            {(!violationStats.trend || violationStats.trend.length === 0) && (
              <div style={{ color: theme === 'light' ? '#23272b' : '#bfc7d5', textAlign: 'center', marginTop: 8, fontSize: '1.02rem' }}>
                {t('dashboard.noRecentViolations')}
              </div>
            )}
          </div>
        </div>
        {/* Bar Chart: Top 5 agents with most violations */}
        <div style={{ gridArea: 'top5chart', minWidth: 320,maxWidth:750, minHeight: 150 }}>
            <div className="chart-container" style={{ borderRadius: 18, padding: 18, boxShadow: '0 2px 16px #4fd1c533', border: '2px solid #4fd1c5', background: theme === 'light' ? '#fff' : '#23272b', minHeight: 120 }}>
              <h3 style={{ color: theme === 'light' ? '#23272b' : '#fff', marginBottom: 12, fontWeight: 700, fontSize: '1.08rem', letterSpacing: 0.5 }}>{t('dashboard.topAgents')}</h3>
              <ResponsiveContainer width="100%" height={100}>
                <BarChart
                  data={violationStats.top_5_agents && violationStats.top_5_agents.length > 0 ? violationStats.top_5_agents : [{ hostname: '', violation_count: 0 }]}
                  margin={{ top: 8, right: 24, left: 0, bottom: 8 }}
                  layout="vertical"
                >
                  <CartesianGrid stroke="#31343a" strokeDasharray="3 3" />
                  <XAxis type="number" stroke="#bfc7d5" fontSize={12} tickLine={false} axisLine={false} allowDecimals={false} />
                  <YAxis dataKey="hostname" type="category" stroke="#bfc7d5" fontSize={12} tickLine={false} axisLine={false} width={90} />
                  <Tooltip
                    cursor={{ fill: "transparent" }}
                    content={({ active, payload }) => {
                      if (!active || !payload || payload.length === 0) return null;
                      return (
                        <div style={{
                          background: theme === 'light' ? '#fff' : '#23272b',
                          border: '1px solid #31343a',
                          padding: '8px',
                          color: theme === 'light' ? '#23272b' : '#fff'
                        }}>
                          <p>{payload[0].payload.hostname}</p>
                          <p>{t('violations.violations')}: {payload[0].value}</p>
                        </div>
                      );
                    }}
                  />
                  <Bar 
                    dataKey="violation_count" 
                    fill="#4fd1c5" 
                    barSize={18} 
                    radius={[8, 8, 8, 8]} 
                    label={{ position: 'right', fill: theme === 'light' ? '#23272b' : '#fff', fontWeight: 700 }}
                    activeBar={{ fill: '#ffd600' }}
                  />
                </BarChart>
              </ResponsiveContainer>
              {(!violationStats.top_5_agents || violationStats.top_5_agents.length === 0) && (
                <div style={{ color: theme === 'light' ? '#23272b' : '#bfc7d5', textAlign: 'center', marginTop: 8, fontSize: '1.02rem' }}>
                  {t('dashboard.noRecentViolations')}
                </div>
              )}
            </div>
        </div>
        {/* Table: 5 most recent violations */}
        <div style={{ gridArea: 'barandtable', minWidth: 320, minHeight: 120 }}>
            <div style={{ borderRadius: 18, padding: 18, boxShadow: '0 2px 16px #f5656533', border: '2px solid #f56565', background: theme === 'light' ? '#fff' : '#23272b', minHeight: 120 }}>
              <h3 style={{ color: theme === 'light' ? '#23272b' : '#fff', marginBottom: 12, fontWeight: 700, fontSize: '1.08rem', letterSpacing: 0.5 }}>{t('dashboard.recentViolations')}</h3>
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', color: theme === 'light' ? '#23272b' : '#f2f3f7', fontSize: '0.98rem' }}>
                  <thead>
                    <tr style={{ background: '#eb5252ff', color: theme === 'light' ? '#000000ff' : '#f4f3f2ff', fontWeight: 700 }}>
                      <th style={{ padding: '6px 8px', textAlign: 'left' }}>{t('violations.time')}</th>
                      <th style={{ padding: '6px 8px', textAlign: 'left' }}>{t('violations.agent')}</th>
                      <th style={{ padding: '6px 8px', textAlign: 'left' }}>{t('violations.rule')}</th>
                      <th style={{ padding: '6px 8px', textAlign: 'left' }}>{t('violations.message')}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recentViolations.length === 0 ? (
                      <tr><td colSpan={5} style={{ color: theme === 'light' ? '#23272b' : '#bfc7d5', textAlign: 'center', padding: 12 }}>{t('dashboard.noRecentViolations')}</td></tr>
                    ) : recentViolations.map((v, idx) => (
                      <tr key={v.id || idx} style={{ borderBottom: '1.5px solid #333' }}>
                        <td style={{ padding: '6px 8px', color: theme === 'light' ? '#23272b' : '#bfc7d5' }}>{v.detected_at ? new Date(v.detected_at).toLocaleString() : ''}</td>
                        <td style={{ padding: '6px 8px', color: theme === 'light' ? '#23272b' : '#fff' }}>{v.agent?.hostname || v.agent_id || ''}</td>
                        <td style={{ padding: '6px 8px', color: theme === 'light' ? '#23272b' : '#fff' }}>{v.rule?.name || v.rule_id || ''}</td>
                        <td style={{ padding: '6px 8px', color: theme === 'light' ? '#23272b' : '#bfc7d5' }}>{v.message}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
        </div>
      </div>
      
      {/* Toast Notifications */}
      {toastMessage && (
        <Toast
          message={toastMessage.message}
          type={toastMessage.type}
          onClose={() => setToastMessage(null)}
        />
      )}
    </div>
  );
}