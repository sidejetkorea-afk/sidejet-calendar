# -*- coding: utf-8 -*-
"""장 일정표(calendar.json) 형식 검사 — 저장소 검사와 사이드젯이 같은 규칙을 씀"""
import re
from datetime import datetime, date, timedelta

TYPES = {"closed", "special"}
TIME_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
EARLIEST, LATEST = "07:00", "20:00"


def _span(v, where, errs, allow_null=False):
    if v is None and allow_null:
        return
    if not (isinstance(v, list) and len(v) == 2 and all(isinstance(t, str) and TIME_RE.match(t) for t in v)):
        errs.append(f"{where}: [\"HH:MM\", \"HH:MM\"] 형식이어야 함 (값: {v!r})")
        return
    a, b = v
    if not (EARLIEST <= a < b <= LATEST):
        errs.append(f"{where}: 시작<끝, {EARLIEST}~{LATEST} 범위여야 함 (값: {v})")


def validate(cal, today=None, years=3):
    """반환: (문제 없는 일정만 남긴 dict, 오류 목록). 오류가 있는 '날'만 버리고 나머지는 살림"""
    errs = []
    if not isinstance(cal, dict) or cal.get("schema") != 1:
        return None, ["schema 가 1 이 아님"]
    today = today or date.today()
    lo, hi = today - timedelta(days=365 * years), today + timedelta(days=365 * years)
    default = cal.get("default") or {}
    for k in ("krx",):
        _span(default.get(k), f"default.{k}", errs)
    for k in ("nxt_pre", "nxt_after"):
        if k in default:
            _span(default[k], f"default.{k}", errs, allow_null=True)
    if errs:
        return None, errs                     # 기본 시간이 틀리면 파일 전체를 쓰지 않음
    clean = {}
    for d, info in (cal.get("days") or {}).items():
        before = len(errs)
        try:
            day = datetime.strptime(d, "%Y-%m-%d").date()
            if not lo <= day <= hi:
                errs.append(f"{d}: 날짜가 허용 범위({lo}~{hi}) 밖")
        except (ValueError, TypeError):
            errs.append(f"{d}: 날짜 형식이 YYYY-MM-DD 가 아님")
            continue
        if not isinstance(info, dict) or info.get("type") not in TYPES:
            errs.append(f"{d}: type 은 closed 또는 special")
            continue
        if not isinstance(info.get("note", ""), str) or len(info.get("note", "")) > 40:
            errs.append(f"{d}: note 는 40자 이하 글자")
        if not isinstance(info.get("confirmed", True), bool):
            errs.append(f"{d}: confirmed 는 true/false")
        if info["type"] == "special":
            _span(info.get("krx"), f"{d}.krx", errs)
            for k in ("nxt_pre", "nxt_after"):
                if k in info:
                    _span(info[k], f"{d}.{k}", errs, allow_null=True)
        if len(errs) == before:
            clean[d] = info
    out = dict(cal)
    out["days"] = clean
    return out, errs
