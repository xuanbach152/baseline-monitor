"""
Script tạo báo cáo tổng hợp compliance.

Usage:
    python scripts/generate_report.py
    python scripts/generate_report.py --agent-id server-01
    python scripts/generate_report.py --format json
    python scripts/generate_report.py --output report.pdf
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import 'app'
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
from datetime import datetime, timedelta
from sqlalchemy import text, func
from app.db.database import SessionLocal
from app.models.agent_report import AgentReport
import json


def get_summary_stats(db, days: int = 7):
    """Lấy thống kê tổng quan."""
    cutoff_date = datetime.now() - timedelta(days=days)
    
    # Total reports
    total_reports = db.query(func.count(AgentReport.id)).filter(
        AgentReport.created_at >= cutoff_date
    ).scalar()
    
    # Unique agents
    unique_agents = db.query(func.count(func.distinct(AgentReport.agent_id))).filter(
        AgentReport.created_at >= cutoff_date
    ).scalar()
    
    # Pass/Fail/Warn counts (parse từ results JSON)
    query = text("""
        SELECT 
            SUM(CASE WHEN result->>'status' = 'pass' THEN 1 ELSE 0 END) as pass_count,
            SUM(CASE WHEN result->>'status' = 'fail' THEN 1 ELSE 0 END) as fail_count,
            SUM(CASE WHEN result->>'status' = 'warn' THEN 1 ELSE 0 END) as warn_count
        FROM agent_reports, 
             jsonb_array_elements(results) as result
        WHERE created_at >= :cutoff_date
    """)
    
    result = db.execute(query, {"cutoff_date": cutoff_date}).fetchone()
    
    return {
        "total_reports": total_reports,
        "unique_agents": unique_agents,
        "pass_count": result[0] or 0,
        "fail_count": result[1] or 0,
        "warn_count": result[2] or 0,
        "period_days": days
    }


def get_agent_report(db, agent_id: str = None):
    """Lấy báo cáo chi tiết theo agent."""
    query = db.query(AgentReport)
    
    if agent_id:
        query = query.filter(AgentReport.agent_id == agent_id)
    
    reports = query.order_by(AgentReport.created_at.desc()).limit(100).all()
    
    return [
        {
            "id": r.id,
            "agent_id": r.agent_id,
            "os_type": r.os_type,
            "created_at": r.created_at.isoformat(),
            "results": r.results
        }
        for r in reports
    ]


def format_text_report(stats: dict, reports: list):
    """Format báo cáo dạng text."""
    output = []
    output.append("="*60)
    output.append("📊 BASELINE MONITOR - COMPLIANCE REPORT")
    output.append("="*60)
    output.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append(f"Period: Last {stats['period_days']} days")
    output.append("")
    
    output.append("📈 SUMMARY STATISTICS")
    output.append("-"*60)
    output.append(f"Total Reports:    {stats['total_reports']}")
    output.append(f"Unique Agents:    {stats['unique_agents']}")
    output.append(f"✅ Passed Rules:  {stats['pass_count']}")
    output.append(f"❌ Failed Rules:  {stats['fail_count']}")
    output.append(f"⚠️  Warning Rules: {stats['warn_count']}")
    
    total_checks = stats['pass_count'] + stats['fail_count'] + stats['warn_count']
    if total_checks > 0:
        compliance_rate = (stats['pass_count'] / total_checks) * 100
        output.append(f"📊 Compliance Rate: {compliance_rate:.1f}%")
    
    output.append("")
    output.append("="*60)
    
    return "\n".join(output)


def format_json_report(stats: dict, reports: list):
    """Format báo cáo dạng JSON."""
    return json.dumps({
        "generated_at": datetime.now().isoformat(),
        "summary": stats,
        "reports": reports
    }, indent=2)


def generate_report(agent_id: str = None, format: str = "text", output: str = None, days: int = 7):
    """Tạo báo cáo."""
    print("📊 Generating compliance report...")
    
    db = SessionLocal()
    try:
        # Get data
        stats = get_summary_stats(db, days)
        reports = get_agent_report(db, agent_id)
        
        # Format report
        if format == "json":
            content = format_json_report(stats, reports)
        else:
            content = format_text_report(stats, reports)
        
        # Output
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content)
            print(f"✅ Report saved to: {output}")
        else:
            print(content)
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        return False
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Generate compliance report")
    parser.add_argument(
        "--agent-id", "-a",
        help="Filter by specific agent ID"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Save report to file"
    )
    parser.add_argument(
        "--days", "-d",
        type=int,
        default=7,
        help="Report period in days (default: 7)"
    )
    
    args = parser.parse_args()
    
    success = generate_report(
        agent_id=args.agent_id,
        format=args.format,
        output=args.output,
        days=args.days
    )
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
