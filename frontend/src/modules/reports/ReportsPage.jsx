import React, { useState } from 'react';
import axios from 'axios';
import { FileText, Download, Calendar, Filter, FileSpreadsheet, AlertCircle } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useTheme } from '../../context/ThemeContext';
import './ReportsPage.css';

const API_URL = import.meta.env.VITE_API_URL;

export default function ReportsPage() {
  const { t } = useTranslation();
  const { theme } = useTheme();
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);
  
  // Form state
  const [reportType, setReportType] = useState('compliance');
  const [format, setFormat] = useState('pdf');
  const [dateFrom, setDateFrom] = useState(() => {
    const date = new Date();
    date.setDate(date.getDate() - 30);
    return date.toISOString().split('T')[0];
  });
  const [dateTo, setDateTo] = useState(() => {
    return new Date().toISOString().split('T')[0];
  });
  const [severity, setSeverity] = useState('all');
  const [resolved, setResolved] = useState('all');

  const handleGenerate = async () => {
    setError(null);
    setGenerating(true);

    try {
      let url = '';
      const params = new URLSearchParams({
        date_from: dateFrom,
        date_to: dateTo
      });

      if (reportType === 'compliance') {
        url = `${API_URL}/reports/compliance/pdf?${params}`;
      } else if (reportType === 'violations') {
        if (severity !== 'all') params.append('severity', severity);
        if (resolved !== 'all') params.append('resolved', resolved === 'true');
        
        if (format === 'csv') {
          url = `${API_URL}/reports/violations/csv?${params}`;
        } else if (format === 'excel') {
          url = `${API_URL}/reports/violations/excel?${params}`;
        }
      }

      // Download file
      const response = await axios.get(url, {
        responseType: 'blob'
      });

      // Get content type from response
      const contentType = response.headers['content-type'];
      
      // Create blob with correct MIME type
      const blob = new Blob([response.data], { type: contentType });
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      
      // Extract filename from Content-Disposition header or generate default
      const contentDisposition = response.headers['content-disposition'];
      let filename = 'report';
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/['"]/g, '');
        }
      } else {
        // Generate filename based on format if no header
        const timestamp = new Date().toISOString().split('T')[0];
        if (reportType === 'compliance') {
          filename = `compliance_report_${timestamp}.pdf`;
        } else if (format === 'csv') {
          filename = `violations_export_${timestamp}.csv`;
        } else if (format === 'excel') {
          filename = `violations_export_${timestamp}.xlsx`;
        }
      }
      
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(link.href);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate report');
      console.error('Report generation error:', err);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className={`reports-page ${theme === 'light' ? 'light-mode' : ''}`}>
      <div className="page-header">
        <h1>
          <FileText size={32} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 12 }} />
          {t('reports.title')}
        </h1>
      </div>

      {error && (
        <div className="error-banner">
          <AlertCircle size={20} />
          {error}
        </div>
      )}

      <div className="reports-container">
        <div className="report-generator-card">
          <h2>{t('reports.generate')}</h2>
          <p className="card-description">
            Create compliance reports or export violation data in various formats
          </p>

          <form onSubmit={(e) => { e.preventDefault(); handleGenerate(); }}>
            {/* Report Type */}
            <div className="form-group">
              <label>
                <FileText size={16} /> {t('reports.reportType')}
              </label>
              <select value={reportType} onChange={(e) => setReportType(e.target.value)}>
                <option value="compliance">{t('reports.complianceSummary')}</option>
                <option value="violations">{t('reports.violationsExport')}</option>
              </select>
            </div>

            {/* Format (only for violations) */}
            {reportType === 'violations' && (
              <div className="form-group">
                <label>
                  <FileSpreadsheet size={16} /> {t('reports.exportFormat')}
                </label>
                <select value={format} onChange={(e) => setFormat(e.target.value)}>
                  <option value="csv">CSV (Comma-Separated Values)</option>
                  <option value="excel">Excel (XLSX)</option>
                </select>
              </div>
            )}

            {/* Date Range */}
            <div className="form-row">
              <div className="form-group">
                <label>
                  <Calendar size={16} /> {t('reports.fromDate')}
                </label>
                <input
                  type="date"
                  value={dateFrom}
                  onChange={(e) => setDateFrom(e.target.value)}
                  max={dateTo}
                  required
                />
              </div>

              <div className="form-group">
                <label>
                  <Calendar size={16} /> {t('reports.toDate')}
                </label>
                <input
                  type="date"
                  value={dateTo}
                  onChange={(e) => setDateTo(e.target.value)}
                  min={dateFrom}
                  required
                />
              </div>
            </div>

            {/* Filters (only for violations) */}
            {reportType === 'violations' && (
              <>
                <div className="form-row">
                  <div className="form-group">
                    <label>
                      <Filter size={16} /> {t('reports.severity')}
                    </label>
                    <select value={severity} onChange={(e) => setSeverity(e.target.value)}>
                      <option value="all">{t('reports.allSeverities')}</option>
                      <option value="critical">{t('common.critical')}</option>
                      <option value="high">{t('common.high')}</option>
                      <option value="medium">{t('common.medium')}</option>
                      <option value="low">{t('common.low')}</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label>
                      <Filter size={16} /> {t('reports.resolutionStatus')}
                    </label>
                    <select value={resolved} onChange={(e) => setResolved(e.target.value)}>
                      <option value="all">{t('reports.allViolations')}</option>
                      <option value="false">{t('reports.unresolvedOnly')}</option>
                      <option value="true">{t('reports.resolvedOnly')}</option>
                    </select>
                  </div>
                </div>
              </>
            )}

            {/* Generate Button */}
            <button type="submit" className="btn-generate" disabled={generating}>
              <Download size={20} />
              {generating ? t('reports.generating') : t('reports.generate')}
            </button>
          </form>
        </div>

        {/* Info Card */}
        <div className="info-card">
          <h3>{t('reports.availableReports')}</h3>
          
          <div className="report-info-item">
            <div className="report-icon">
              <FileText size={24} />
            </div>
            <div className="report-info-content">
              <h4>{t('reports.complianceSummaryTitle')}</h4>
              <p>
                {t('reports.complianceSummaryDesc')}
              </p>
            </div>
          </div>

          <div className="report-info-item">
            <div className="report-icon">
              <FileSpreadsheet size={24} />
            </div>
            <div className="report-info-content">
              <h4>{t('reports.violationsExportTitle')}</h4>
              <p>
                {t('reports.violationsExportDesc')}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
