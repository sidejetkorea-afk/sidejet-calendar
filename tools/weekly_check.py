# -*- coding: utf-8 -*-
"""
주간 점검 (매주 월요일 GitHub Actions 가 실행) — 고칠 것이 있으면 report.md 를 만들고,
워크플로가 그 내용으로 '[점검] 일정표 확인 필요' 이슈를 엽니다.

점검 내용
  1) 30일 안에 '예상(confirmed: false)' 일정이 남아 있음 → 거래소 공고 확인 필요
  2) 11월 15일 이후인데 다음 해 휴장일이 없음
  3) 실제 배포된 파일의 서명이 pubkeys.txt 와 맞지 않거나, 저장소 내용과 다름(배포 실패)
"""
import argparse
import json
import os
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from calendar_lib import read_pubkeys, validate_calendar, verify_calendar_signature  # noqa: E402
from validate_calendar import load  # noqa: E402

KST = timezone(timedelta(hours=9))


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "sidejet-calendar-check", "Cache-Control": "no-cache"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()


def default_url():
    repo = os.environ.get("GITHUB_REPOSITORY", "sidejetkorea-afk/sidejet-calendar")
    owner, name = repo.split("/", 1)
    return f"https://{owner}.github.io/{name}/sidejet/calendar.json"


def comparable(cal):
    return json.dumps({k: cal[k] for k in ("default", "days", "notice")}, sort_keys=True, default=list)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--url", default="")
    ap.add_argument("--report", default="report.md")
    ap.add_argument("--today", default="")
    args = ap.parse_args()
    today = datetime.strptime(args.today, "%Y-%m-%d").date() if args.today else datetime.now(KST).date()
    problems = []

    obj, err = load(os.path.join(args.repo, "calendar.json"))
    cal = None
    if err:
        problems.append(f"calendar.json 문법 오류 — {err.splitlines()[0]}")
    else:
        cal, errors, _w = validate_calendar(obj)
        if cal is None or errors:
            problems.append("calendar.json 형식 오류 — " + "; ".join(errors))
            cal = None

    if cal:
        soon = [(k, d) for k, d in sorted(cal["days"].items())
                if not d["confirmed"] and today <= datetime.strptime(k, "%Y-%m-%d").date() <= today + timedelta(days=30)]
        for k, d in soon:
            problems.append(f"{k} ({d['note']}) 이(가) 아직 '예상' 일정입니다 — 거래소 공고를 확인하고 "
                            "시간을 맞춘 뒤 `\"confirmed\": true` 로 바꾸세요")
        if (today.month, today.day) >= (11, 15):
            nxt = str(today.year + 1)
            n = sum(1 for k, d in cal["days"].items()
                    if k.startswith(nxt) and k != f"{nxt}-01-01" and d["type"] == "closed")
            if n == 0:
                problems.append(f"{nxt}년 휴장일이 아직 없습니다 — 12월에 거래소가 공고하면 1년치를 넣으세요")

    url = args.url or default_url()
    pubs = read_pubkeys(os.path.join(args.repo, "pubkeys.txt"))
    try:
        raw = fetch(url)
        sig = fetch(url + ".sig").decode("utf-8")
        if not pubs:
            problems.append("pubkeys.txt 에 공개키가 없어 배포 파일 서명을 확인할 수 없습니다")
        elif verify_calendar_signature(raw, sig, pubs) is None:
            problems.append(f"배포된 파일의 서명이 pubkeys.txt 공개키와 맞지 않습니다 ({url}) — "
                            "사이드젯이 이 일정을 거부합니다. 비밀값 SIDEJET_SIGNING_KEY 와 pubkeys.txt 가 같은 짝인지 확인")
        deployed, derr, _w = validate_calendar(json.loads(raw.decode("utf-8")))
        if deployed is None:
            problems.append("배포된 파일 형식 오류 — " + "; ".join(derr))
        elif cal and comparable(deployed) != comparable(cal):
            problems.append("배포된 일정이 저장소의 calendar.json 과 다릅니다 — Actions 탭에서 마지막 배포가 "
                            "실패했는지 확인하고 Run workflow 로 다시 배포하세요")
    except Exception as e:
        problems.append(f"배포된 파일을 받지 못했습니다 ({url}) — {type(e).__name__}: {e}")

    if problems:
        body = (f"주간 점검 결과 ({today}) — 아래를 확인해 주세요.\n\n"
                + "\n".join(f"- [ ] {p}" for p in problems)
                + "\n\n고친 뒤 이 이슈를 닫으면 됩니다. 다음 점검은 다음 주 월요일입니다.\n")
        with open(args.report, "w", encoding="utf-8") as f:
            f.write(body)
        print(body)
    else:
        if os.path.exists(args.report):
            os.remove(args.report)
        print(f"점검 통과 ({today})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
