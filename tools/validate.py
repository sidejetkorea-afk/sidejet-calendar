# -*- coding: utf-8 -*-
"""사용법: python tools/validate.py calendar.json  — 문제가 하나라도 있으면 실패(배포 중단)"""
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from calendar_lib import validate

path = sys.argv[1] if len(sys.argv) > 1 else "calendar.json"
try:
    with open(path, encoding="utf-8") as f:
        cal = json.load(f)
except ValueError as e:
    print(f"JSON 문법 오류: {e}")
    sys.exit(1)
clean, errs = validate(cal)
if errs:
    print("일정표 오류:")
    for e in errs:
        print("  -", e)
    sys.exit(1)
days = clean["days"]
print(f"OK — 일정 {len(days)}일 (휴장 {sum(1 for v in days.values() if v['type'] == 'closed')}, "
      f"시간 변경 {sum(1 for v in days.values() if v['type'] == 'special')}, "
      f"미확정 {sum(1 for v in days.values() if not v.get('confirmed', True))})")
