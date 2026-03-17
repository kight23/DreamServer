#!/usr/bin/env python3
\"\"\"Email Alert Sender for Motion Guard.
Usage: python send_email.py --config=config.yaml --screenshot=alert.jpg --subject=\\\"Motion Detected\\\"

Integrates with motion_detector.py.\"\"\"

import smtplib
import argparse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
import yaml
import os
from pathlib import Path

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def send_motion_email(config_path, screenshot_path, subject=\"Motion Detected - IMOU A2-L-D463\"):
    config = load_config(config_path)
    alerts = config['alerts']
    
    msg = MIMEMultipart()
    msg['From'] = alerts['email_from']
    msg['To'] = alerts['email_to']
    msg['Subject'] = subject
    
    # Email body
    body = f\"\"\"🚨 MOTION ALERT 🚨

Camera: {config['camera']['name']}
Time: {Path(screenshot_path).stem}
Screenshot attached.

View live: {config['camera']['rtsp_url']}
Dashboard: http://localhost:3001
\"\"\"
    msg.attach(MIMEText(body, 'plain'))
    
    # Attach screenshot
    with open(screenshot_path, 'rb') as f:
        img = MIMEImage(f.read())
        img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(screenshot_path))
        msg.attach(img)
    
    # Send
    server = smtplib.SMTP(alerts['smtp_server'], alerts['smtp_port'])
    server.starttls()
    server.login(alerts['smtp_user'], alerts['smtp_password'])
    server.send_message(msg)
    server.quit()
    
    print(f\"📧 Email sent to {alerts['email_to']}\")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='../config/motion-guard/config.yaml')
    parser.add_argument('--screenshot')
    parser.add_argument('--subject', default='Motion Detected')
    args = parser.parse_args()
    
    send_motion_email(args.config, args.screenshot, args.subject)
