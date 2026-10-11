# -*- coding: utf-8 -*-
"""
calendar.json 형식 검사
  python3 tools/validate_calendar.py calendar.json
오류가 있으면 GitHub Actions 화면에 빨간 글씨로 보이고, 배포가 멈춥니다(이전 일정은 그대로 유지).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from calendar_lib import validate_calendar  # noqa: E402


def load(path):
    """JSON 읽기 — 문법 오류면 몇 번째 줄인지 알려줌"""
    with open(path, encoding="utf-8-sig") as f:
        text = f.read()
    try:
        return json.loads(text), None
    except json.JSONDecodeError as e:
        line = text.splitlines()[e.lineno - 1] if 0 < e.lineno <= len(text.splitlines()) else ""
        hint = ""
        if "Expecting ',' delimiter" in e.msg or "Expecting property name" in e.msg:
            hint = " (바로 앞 줄 끝의 쉼표(,)가 빠졌거나 마지막 항목 뒤에 쉼표가 남았는지 확인)"
        return None, f"JSON 문법 오류 {e.lineno}번째 줄 {e.colno}번째 글자: {e.msg}{hint}\n    → {line.strip()}"


def main(path):
    obj, err = load(path)
    if err:
        print(f"::error file={os.path.basename(path)}::{err.splitlines()[0]}")
        print(err)
        return 1
    clean, errors, warns = validate_calendar(obj)
    for w in warns:
        print(f"::warning file={os.path.basename(path)}::{w}")
    if clean is None or errors:
        for e in errors:
            print(f"::error file={os.path.basename(path)}::일정표 오류: {e}")
        print(f"\n일정표 오류 {len(errors)}건 — 위 내용을 고친 뒤 다시 Commit 하세요.")
        return 1
    n_closed = sum(1 for d in clean["days"].values() if d["type"] == "closed")
    n_special = len(clean["days"]) - n_closed
    unconfirmed = [k for k, d in sorted(clean["days"].items()) if not d["confirmed"]]
    print(f"검사 통과 — 휴장 {n_closed}일, 거래시간 변경 {n_special}일"
          + (f", 예상 일정 {len(unconfirmed)}건({', '.join(unconfirmed)})" if unconfirmed else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "calendar.json"))
