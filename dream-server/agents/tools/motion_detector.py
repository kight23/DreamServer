#!/usr/bin/env python3
\"\"\"Motion Detection for IMOU A2-L-D463 RTSP stream.
Usage: python motion_detector.py --mode=continuous [--config=config.yaml]
Integrates with OpenClaw agent via exec tool.\"\"\"

import argparse
import cv2
import numpy as np
import yaml
import os
import time
from datetime import datetime
import json
from pathlib import Path

# Default config (override from YAML)
DEFAULT_CONFIG = {
    'camera': {
        'rtsp_url': 'rtsp://admin:L238A4A4@192.168.1.199:554/cam/realmonitor?channel=1&subtype=0',
        'width': 640,
        'height': 480
    },
    'motion_detection': {
        'threshold': 25,
        'min_area': 500,
        'cooldown': 30
    },
    'alerts': {
        'screenshot_dir': './alerts',
        'clip_duration': 10
    }
}

def load_config(config_path='config/motion-guard/config.yaml'):
    config = DEFAULT_CONFIG.copy()
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            user_config = yaml.safe_load(f) or {}
            config.update(user_config)
    return config

def send_alert(config, frame, motion_area):
    \"\"\"Save screenshot + metadata. Agent sẽ handle email.\"\"\"
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    alert_dir = Path(config['alerts']['screenshot_dir'])
    alert_dir.mkdir(exist_ok=True)
    
    filename = f\"motion_alert_{timestamp}.jpg\"
    filepath = alert_dir / filename
    
    cv2.imwrite(str(filepath), frame)
    
    # Log metadata JSON
    metadata = {
        'timestamp': timestamp,
        'motion_area': motion_area,
        'camera': config['camera']['name']
    }
    (alert_dir / f\"{filename}.json\").write_text(json.dumps(metadata))
    
    print(f\"🚨 ALERT: Motion detected! Screenshot: {filepath}\")
    return str(filepath)

def motion_detector(rtsp_url, config):
    \"\"\"Main motion detection loop.\"\"\"
    cap = cv2.VideoCapture(rtsp_url)
    
    if not cap.isOpened():
        print(\"❌ Cannot connect to camera!\")
        return False
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config['camera']['width'])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config['camera']['height'])
    
    ret, frame1 = cap.read()
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray1 = cv2.GaussianBlur(gray1, (21, 21), 0)
    
    print(\"👁️ Monitoring started...\")
    
    last_alert = 0
    while True:
        ret, frame2 = cap.read()
        if not ret:
            print(\"⚠️ Stream interrupted, reconnecting...\")
            time.sleep(5)
            continue
            
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.GaussianBlur(gray2, (21, 21), 0)
        
        delta = cv2.absdiff(gray1, gray2)
        thresh = cv2.threshold(delta, config['motion_detection']['threshold'], 255, cv2.THRESH_BINARY)[1]
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        motion_detected = False
        for contour in contours:
            if cv2.contourArea(contour) < config['motion_detection']['min_area']:
                continue
            motion_detected = True
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame2, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        if motion_detected and (time.time() - last_alert) > config['motion_detection']['cooldown']:
            filepath = send_alert(config, frame2, len(contours))
            print(f\"📸 Screenshot saved: {filepath}\")
            last_alert = time.time()
        
        gray1 = gray2.copy()
        
        # Show preview (optional)
        cv2.imshow('Motion Guard', frame2)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == \"__main__\":
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', default='test', choices=['test', 'continuous'])
    parser.add_argument('--duration', type=int, default=30, help='Test duration seconds')
    parser.add_argument('--config', default='config/motion-guard/config.yaml')
    args = parser.parse_args()
    
    config = load_config(args.config)
    rtsp_url = config['camera']['rtsp_url']
    
    if args.mode == 'test':
        print(f\"🧪 Test mode: {args.duration}s\")
        # Simplified test loop
        motion_detector(rtsp_url, config)
    else:
        print(\"🔄 Continuous monitoring (Ctrl+C to stop)\")
        motion_detector(rtsp_url, config)
