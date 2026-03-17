# Motion Guard Agent for OpenClaw - Task Progress Tracker

✅ **Step 1 COMPLETE:** Created TODO.md

## Approved Plan Steps:
1. ✅ Tạo directory `agents/tools/` và `config/motion-guard/`
2. ✅ **Tạo `agents/templates/motion-guard.yaml`** (agent template) - User approved with email alerts
3. [ ] Tạo `agents/tools/motion_detector.py` 
4. [ ] Tạo `agents/tools/daily_report.py`
5. [ ] Update `config/motion-guard/config.yaml` với email settings
6. [ ] Test: docker compose restart openclaw && /agent load motion-guard
7. [ ] Validation + demo

**Next step: 2/7 - Tạo motion_detector.py (OpenCV RTSP motion detection)**

**Alert channel:** Email (sẽ config SMTP sau)
**Camera RTSP:** rtsp://admin:L238A4A4@192.168.1.199:554/cam/realmonitor?channel=1&subtype=0
