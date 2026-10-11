# -*- coding: utf-8 -*-
"""
배포 파일 만들기 (GitHub Actions 가 실행)
  SIDEJET_SIGNING_KEY=<개인키> python3 tools/build_site.py --repo . --out site

만드는 파일
  site/sidejet/calendar.json      사이드젯이 받아 가는 일정 (작성 시각 updated 자동 기록)
  site/sidejet/calendar.json.sig  위 파일의 Ed25519 서명
  site/sidejet/pubkeys.txt        공개키 (참고용)
  site/calendar/index.html        사람이 보는 일정 페이지
  site/index.html                 일정 페이지로 이동
"""
import argparse
import base64
import html
import json
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from calendar_lib import Ed25519, read_pubkeys, validate_calendar  # noqa: E402
from validate_calendar import load  # noqa: E402

KST = timezone(timedelta(hours=9))
WEEKDAY_KO = "월화수목금토일"


def fail(msg):
    print(f"::error::{msg}")
    sys.exit(1)


def signing_seed():
    key = os.environ.get("SIDEJET_SIGNING_KEY", "").strip()
    if not key:
        fail("SIDEJET_SIGNING_KEY 가 없어 서명할 수 없습니다 — 저장소 Settings → Secrets and variables → "
             "Actions 에 개인키를 등록하세요")
    try:
        seed = base64.b64decode(key, validate=True)
    except Exception:
        seed = b""
    if len(seed) != 32:
        fail("SIDEJET_SIGNING_KEY 값이 올바른 개인키가 아닙니다 (44글자 base64) — 복사할 때 잘리지 않았는지 확인")
    return seed


def page_html(cal, pub_fps, repo_url):
    today = datetime.now(KST).date()
    rows_up, rows_past = [], []
    for key, d in sorted(cal["days"].items()):
        day = datetime.strptime(key, "%Y-%m-%d").date()
        kind = "휴장" if d["type"] == "closed" else "거래시간 변경"
        hours = "—" if d["type"] == "closed" else f"{d['krx'][0]} ~ {d['krx'][1]}"
        extra = []
        if d["type"] == "special":
            if d.get("nxt_pre") is None:
                extra.append("NXT 프리마켓 없음")
            if isinstance(d.get("nxt_after"), tuple):
                extra.append(f"NXT 애프터 {d['nxt_after'][0]}~{d['nxt_after'][1]}")
        tag = "" if d["confirmed"] else '<span class="tag">예상</span>'
        cls = "closed" if d["type"] == "closed" else "special"
        tr = (f'<tr class="{cls}"><td>{key} ({WEEKDAY_KO[day.weekday()]})</td><td>{kind} {tag}</td>'
              f'<td>{hours}</td><td>{html.escape(d["note"])}</td><td>{html.escape(", ".join(extra))}</td></tr>')
        (rows_up if day >= today else rows_past).append(tr)
    dflt = cal["default"]
    head = "<tr><th>날짜</th><th>구분</th><th>KRX 정규장</th><th>내용</th><th>NXT</th></tr>"
    up = "\n".join(rows_up) or '<tr><td colspan="5">등록된 일정 없음</td></tr>'
    past = "\n".join(reversed(rows_past)) or '<tr><td colspan="5">없음</td></tr>'
    return f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>사이드젯 장 일정</title>
<style>
 :root {{ --bg:#fafafa; --fg:#1d1d1f; --mute:#6b6b70; --line:#e2e2e6; --closed:#f4f4f6; --special:#fff7e0; --tag:#ef6c00; }}
 @media (prefers-color-scheme: dark) {{ :root {{ --bg:#16171b; --fg:#e8e8ea; --mute:#9a9aa2; --line:#2c2d33; --closed:#202127; --special:#2b2617; --tag:#ffb74d; }} }}
 body {{ margin:0; background:var(--bg); color:var(--fg); font:15px/1.55 -apple-system,"Malgun Gothic","Apple SD Gothic Neo",sans-serif; }}
 main {{ max-width:860px; margin:0 auto; padding:24px 16px 48px; }}
 h1 {{ font-size:22px; margin:0 0 4px; }} h2 {{ font-size:17px; margin:28px 0 8px; }}
 p.meta {{ color:var(--mute); margin:0 0 16px; font-size:13px; }}
 .wrap {{ overflow-x:auto; }}
 table {{ border-collapse:collapse; width:100%; min-width:560px; }}
 th, td {{ text-align:left; padding:8px 10px; border-bottom:1px solid var(--line); vertical-align:top; }}
 th {{ font-size:13px; color:var(--mute); font-weight:600; }}
 td:first-child, td:nth-child(3) {{ white-space:nowrap; }}
 tr.closed td {{ background:var(--closed); }} tr.special td {{ background:var(--special); }}
 .tag {{ color:var(--tag); font-size:12px; font-weight:700; margin-left:4px; }}
 details {{ margin-top:12px; }} code {{ font-size:12px; word-break:break-all; }}
 a {{ color:inherit; }}
</style></head>
<body><main>
<h1>사이드젯 장 일정</h1>
<p class="meta">평소: KRX {dflt['krx'][0]}~{dflt['krx'][1]} · NXT 프리 {dflt['nxt_pre'][0]}~{dflt['nxt_pre'][1]},
 애프터 {dflt['nxt_after'][0]}~{dflt['nxt_after'][1]} · 주말 휴장<br>
작성 {html.escape(cal['updated'])} · 평소와 다른 날만 적었습니다. <b>예상</b>은 거래소 공고 전 값입니다.</p>
<h2>앞으로</h2>
<div class="wrap"><table>{head}
{up}
</table></div>
<details><summary>지난 일정</summary>
<div class="wrap"><table>{head}
{past}
</table></div></details>
<h2>틀린 일정을 봤다면</h2>
<p><a href="{repo_url}/issues/new?template=calendar-error.yml">일정 오류 신고</a> (GitHub 로그인 필요)</p>
<details><summary>기술 정보</summary>
<p>사이드젯은 <code>sidejet/calendar.json</code> 과 서명 <code>calendar.json.sig</code> 를 받아
 아래 공개키로 서명을 확인한 뒤에만 씁니다.</p>
<p>{'<br>'.join(f'<code>{html.escape(k)}</code>' for k in pub_fps) or '공개키 미등록'}</p>
</details>
</main></body></html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--out", default="site")
    args = ap.parse_args()

    obj, err = load(os.path.join(args.repo, "calendar.json"))
    if err:
        fail(err.splitlines()[0])
    clean, errors, warns = validate_calendar(obj)
    if clean is None or errors:
        fail("일정표 오류: " + "; ".join(errors))
    for w in warns:
        print(f"::warning::{w}")

    seed = signing_seed()
    pub = base64.b64encode(Ed25519.public_key(seed)).decode()
    pubs = read_pubkeys(os.path.join(args.repo, "pubkeys.txt"))
    if pubs and pub not in pubs:
        fail("SIDEJET_SIGNING_KEY(개인키)가 pubkeys.txt 의 공개키와 짝이 아닙니다 — "
             "같은 때 만든 키인지 확인하세요 (사이드젯이 서명을 거부하게 됩니다)")
    if not pubs:
        print("::warning::pubkeys.txt 에 공개키가 없습니다 — 키 짝 확인과 주간 점검을 하려면 공개키를 넣으세요")

    out_obj = {
        "schema": obj["schema"],
        "updated": datetime.now(KST).isoformat(timespec="seconds"),
        "default": obj.get("default", {}),
        "days": {k: obj["days"][k] for k in sorted(obj.get("days", {}))},
        "notice": obj.get("notice", {"text": "", "url": "", "min_app_version": ""}),
    }
    raw = (json.dumps(out_obj, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
    sig = Ed25519.sign(seed, raw)
    if not Ed25519.verify(Ed25519.public_key(seed), raw, sig):
        fail("서명 자체 확인 실패 (이 메시지가 보이면 tools 를 다시 받으세요)")

    os.makedirs(os.path.join(args.out, "sidejet"), exist_ok=True)
    os.makedirs(os.path.join(args.out, "calendar"), exist_ok=True)
    with open(os.path.join(args.out, "sidejet", "calendar.json"), "wb") as f:
        f.write(raw)
    with open(os.path.join(args.out, "sidejet", "calendar.json.sig"), "w", encoding="utf-8") as f:
        f.write(base64.b64encode(sig).decode() + "\n")
    with open(os.path.join(args.out, "sidejet", "pubkeys.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(pubs or [pub]) + "\n")
    repo = os.environ.get("GITHUB_REPOSITORY", "sidejetkorea-afk/sidejet-calendar")
    final, _e, _w = validate_calendar(json.loads(raw.decode("utf-8")))
    with open(os.path.join(args.out, "calendar", "index.html"), "w", encoding="utf-8") as f:
        f.write(page_html(final, pubs or [pub], f"https://github.com/{repo}"))
    with open(os.path.join(args.out, "index.html"), "w", encoding="utf-8") as f:
        f.write('<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=calendar/">'
                '<title>사이드젯 장 일정</title><a href="calendar/">사이드젯 장 일정</a>\n')
    open(os.path.join(args.out, ".nojekyll"), "w").close()
    print(f"배포 파일 생성 완료 — {out_obj['updated']} · 일정 {len(out_obj['days'])}건 · 서명 공개키 {pub[:12]}…")


if __name__ == "__main__":
    main()
