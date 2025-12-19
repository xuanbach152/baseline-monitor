"""
Report generation service for compliance and violations
"""

from datetime import datetime, timedelta
from typing import Optional, List
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.modules.violations.models import Violation
from app.modules.agents.models import Agent
from app.modules.rules.models import Rule


class ReportGenerator:
    """Generate various compliance and violation reports"""
    
    @staticmethod
    def generate_compliance_pdf(
        db: Session,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> bytes:
        """
        Generate a comprehensive compliance report in PDF format
        
        Args:
            db: Database session
            date_from: Start date for report (default: 30 days ago)
            date_to: End date for report (default: now)
            
        Returns:
            PDF file as bytes
        """
        if date_from is None:
            date_from = datetime.now() - timedelta(days=30)
        if date_to is None:
            date_to = datetime.now()
        
        # Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                               leftMargin=0.75*inch, rightMargin=0.75*inch,
                               topMargin=1*inch, bottomMargin=0.75*inch)
        
        # Container for PDF elements
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#d32f2f'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1a1d23'),
            spaceAfter=12,
            spaceBefore=20
        )
        
        # Title
        title = Paragraph("CIS Compliance Report", title_style)
        elements.append(title)
        
        # Report period
        period_text = f"Report Period: {date_from.strftime('%Y-%m-%d')} to {date_to.strftime('%Y-%m-%d')}"
        elements.append(Paragraph(period_text, styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Executive Summary
        elements.append(Paragraph("Executive Summary", heading_style))
        
        # Get statistics
        total_agents = db.query(Agent).count()
        online_agents = db.query(Agent).filter(Agent.is_online == True).count()
        total_rules = db.query(Rule).count()
        active_rules = db.query(Rule).filter(Rule.active == True).count()
        
        violations_query = db.query(Violation).filter(
            Violation.detected_at >= date_from,
            Violation.detected_at <= date_to
        )
        total_violations = violations_query.count()
        resolved_violations = violations_query.filter(
            Violation.resolved_at.isnot(None)
        ).count()
        
        # Summary table
        summary_data = [
            ['Metric', 'Value'],
            ['Total Agents', str(total_agents)],
            ['Online Agents', str(online_agents)],
            ['Total Rules', str(total_rules)],
            ['Active Rules', str(active_rules)],
            ['Total Violations', str(total_violations)],
            ['Resolved Violations', str(resolved_violations)],
            ['Unresolved Violations', str(total_violations - resolved_violations)],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d32f2f')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 0.4*inch))
        
        # Violations by Severity
        elements.append(Paragraph("Violations by Severity", heading_style))
        
        severity_stats = db.query(
            Rule.severity,
            func.count(Violation.id).label('count')
        ).join(Violation, Violation.rule_id == Rule.id).filter(
            Violation.detected_at >= date_from,
            Violation.detected_at <= date_to
        ).group_by(Rule.severity).all()
        
        severity_data = [['Severity', 'Count']]
        for severity, count in severity_stats:
            severity_data.append([severity.upper() if severity else 'UNKNOWN', str(count)])
        
        if len(severity_data) > 1:
            severity_table = Table(severity_data, colWidths=[3*inch, 2*inch])
            severity_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff1744')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(severity_table)
        else:
            elements.append(Paragraph("No violations found in this period.", styles['Normal']))
        
        elements.append(Spacer(1, 0.4*inch))
        
        # Top 10 Agents with Most Violations
        elements.append(Paragraph("Top 10 Agents with Most Violations", heading_style))
        
        top_agents = db.query(
            Agent.hostname,
            func.count(Violation.id).label('violation_count')
        ).join(Violation, Violation.agent_id == Agent.id).filter(
            Violation.detected_at >= date_from,
            Violation.detected_at <= date_to
        ).group_by(Agent.id, Agent.hostname).order_by(
            func.count(Violation.id).desc()
        ).limit(10).all()
        
        agent_data = [['Agent Hostname', 'Violation Count']]
        for hostname, count in top_agents:
            agent_data.append([hostname or 'Unknown', str(count)])
        
        if len(agent_data) > 1:
            agent_table = Table(agent_data, colWidths=[3*inch, 2*inch])
            agent_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff5252')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(agent_table)
        else:
            elements.append(Paragraph("No agent data available.", styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
    
    @staticmethod
    def generate_violations_csv(
        db: Session,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        severity: Optional[str] = None,
        resolved: Optional[bool] = None
    ) -> bytes:
        """
        Generate violations export in CSV format
        
        Args:
            db: Database session
            date_from: Start date filter
            date_to: End date filter
            severity: Filter by severity (critical, high, medium, low)
            resolved: Filter by resolution status (True/False/None for all)
            
        Returns:
            CSV file as bytes
        """
        if date_from is None:
            date_from = datetime.now() - timedelta(days=30)
        if date_to is None:
            date_to = datetime.now()
        
        # Build query
        query = db.query(Violation).filter(
            Violation.detected_at >= date_from,
            Violation.detected_at <= date_to
        )
        
        if resolved is True:
            query = query.filter(Violation.resolved_at.isnot(None))
        elif resolved is False:
            query = query.filter(Violation.resolved_at.is_(None))
        
        violations = query.all()
        
        # Prepare data
        data = []
        for v in violations:
            # Filter by severity if provided
            if severity and v.rule and v.rule.severity != severity:
                continue
                
            data.append({
                'Violation ID': v.id,
                'Detected At': v.detected_at.strftime('%Y-%m-%d %H:%M:%S') if v.detected_at else '',
                'Agent': v.agent.hostname if v.agent else v.agent_id,
                'Rule ID': v.rule.id if v.rule else v.rule_id,
                'Rule Name': v.rule.name if v.rule else '',
                'Severity': v.rule.severity.upper() if v.rule and v.rule.severity else '',
                'Message': v.message or '',
                'Confidence Score': v.confidence_score or 0,
                'Resolved': 'Yes' if v.resolved_at else 'No',
                'Resolved At': v.resolved_at.strftime('%Y-%m-%d %H:%M:%S') if v.resolved_at else '',
                'Resolved By': v.resolved_by or '',
                'Resolution Notes': v.resolution_notes or ''
            })
        
        # Convert to DataFrame and CSV
        df = pd.DataFrame(data)
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        return buffer.getvalue().encode('utf-8')
    
    @staticmethod
    def generate_violations_excel(
        db: Session,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        severity: Optional[str] = None,
        resolved: Optional[bool] = None
    ) -> bytes:
        """
        Generate violations export in Excel format
        
        Args:
            db: Database session
            date_from: Start date filter
            date_to: End date filter
            severity: Filter by severity
            resolved: Filter by resolution status
            
        Returns:
            Excel file as bytes
        """
        if date_from is None:
            date_from = datetime.now() - timedelta(days=30)
        if date_to is None:
            date_to = datetime.now()
        
        # Build query
        query = db.query(Violation).filter(
            Violation.detected_at >= date_from,
            Violation.detected_at <= date_to
        )
        
        if resolved is True:
            query = query.filter(Violation.resolved_at.isnot(None))
        elif resolved is False:
            query = query.filter(Violation.resolved_at.is_(None))
        
        violations = query.all()
        
        # Prepare data
        data = []
        for v in violations:
            # Filter by severity if provided
            if severity and v.rule and v.rule.severity != severity:
                continue
                
            data.append({
                'Violation ID': v.id,
                'Detected At': v.detected_at.strftime('%Y-%m-%d %H:%M:%S') if v.detected_at else '',
                'Agent': v.agent.hostname if v.agent else v.agent_id,
                'Rule ID': v.rule.id if v.rule else v.rule_id,
                'Rule Name': v.rule.name if v.rule else '',
                'Severity': v.rule.severity.upper() if v.rule and v.rule.severity else '',
                'Message': v.message or '',
                'Confidence Score': v.confidence_score or 0,
                'Resolved': 'Yes' if v.resolved_at else 'No',
                'Resolved At': v.resolved_at.strftime('%Y-%m-%d %H:%M:%S') if v.resolved_at else '',
                'Resolved By': v.resolved_by or '',
                'Resolution Notes': v.resolution_notes or ''
            })
        
        # Convert to DataFrame and Excel
        df = pd.DataFrame(data)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Violations', index=False)
        
        buffer.seek(0)
        return buffer.getvalue()
