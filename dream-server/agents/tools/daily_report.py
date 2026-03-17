#!/usr/bin/env python3
\"\"\"Daily Motion Report Generator.
Run via cron or agent: python daily_report.py
Outputs JSON + HTML report.\"\"\"

import json
from pathlib import Path
from datetime import datetime, timedelta
import yaml
import os

def load_config(config_path='config/motion-guard/config.yaml'):
    default = {
        'reports': {'report_dir': './reports', 'retention_days': 30},
        'camera': {'name': 'IMOU A2-L-D463'}
    }
    if os.path.exists(config_path):
        with open(config_path) as f:
            cfg = yaml.safe_load(f) or {}
            default.update(cfg)
    return default

def generate_daily_report(config):
    report_dir = Path(config['reports']['report_dir'])
    report_dir.mkdir(exist_ok=True)
    
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Scan alerts from last 24h
    alerts = []
    alert_dir = Path(config['alerts']['screenshot_dir'])
    
    for alert_file in alert_dir.glob('motion_alert_*.jpg'):
        metadata_file = alert_file.with_suffix('.json')
        if metadata_file.exists():
            mtime = datetime.fromtimestamp(alert_file.stat().st_mtime)
            if yesterday <= mtime.strftime('%Y-%m-%d') <= today:
                with open(metadata_file) as f:
                    data = json.load(f)
                data['screenshot'] = str(alert_file.relative_to(Path.cwd()))
                alerts.append(data)
    
    # Summary stats
    summary = {
        'date': today,
        'camera': config['camera']['name'],
        'total_alerts': len(alerts),
        'peak_hour': max((int(a['timestamp'][9:11]) for a in alerts), default=0),
        'alerts': alerts,
        'generated_at': datetime.now().isoformat()
    }
    
    # Save JSON
    json_path = report_dir / f\"daily_report_{today}.json\"
    json_path.write_text(json.dumps(summary, indent=2))
    
    # Simple HTML report
    html_path = report_dir / f\"daily_report_{today}.html\"
    html = f\"\"\"<html>
<head><title>Motion Guard Report - {today}</title>
<style>body{{font-family:Arial}} table{{border-collapse:collapse}} th,td{{border:1px solid #ddd;padding:8px}}</style></head>
<body>
<h1>📊 Daily Report: {config['camera']['name']}</h1>
<p><strong>{summary['total_alerts']} motion events detected</strong> | Peak: {summary['peak_hour']}:00</p>
<table>
<tr><th>Time</th><th>Motion Area</th><th>Screenshot</th></tr>
{''.join(f'<tr><td>{a[\"timestamp\"][:16]}</td><td>{a[\"motion_area\"]}</td><td><img src=\"{a[\"screenshot\"]}\" width=200></td></tr>' for a in summary['alerts'])}
</table>
</body></html>\"\"\"
    html_path.write_text(html)
    
    print(f\"📈 Daily report generated: {json_path} + {html_path}\")
    print(f\"Summary: {summary['total_alerts']} alerts on {today}\")

if __name__ == '__main__':
    config = load_config()
    generate_daily_report(config)
