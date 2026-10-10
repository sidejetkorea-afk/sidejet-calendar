# -*- coding: utf-8 -*-
"""배포용 폴더 만들기: 검사 → 서명 → 사람용 일정 페이지 생성
사용법: SIDEJET_SIGNING_KEY=<개인키> python tools/build_site.py calendar.json _site
"""
import base64
import html
import json
import os
import sys
from datetime import date, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from calendar_lib import validate
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

src, out = sys.argv[1], sys.argv[2]
raw = open(src, "rb").read()
cal = json.loads(raw)
clean, errs = validate(cal)
if errs:
    print("\n".join(errs))
    sys.exit(1)

key_b64 = os.environ.get("SIDEJET_SIGNING_KEY", "").strip()
if not key_b64:
    print("SIDEJET_SIGNING_KEY 가 없어 서명할 수 없습니다.")
    sys.exit(1)
key = Ed25519PrivateKey.from_private_bytes(base64.b64decode(key_b64))
sig = base64.b64encode(key.sign(raw)).decode()        # 받은 그대로의 바이트에 서명

os.makedirs(os.path.join(out, "sidejet"), exist_ok=True)
os.makedirs(os.path.join(out, "calendar"), exist_ok=True)
open(os.path.join(out, "sidejet", "calendar.json"), "wb").write(raw)
open(os.path.join(out, "sidejet", "calendar.json.sig"), "w").write(sig)

# ---- 사람이 읽는 일정 페이지 ----
WD = "월화수목금토일"
d0 = clean["default"]["krx"]
rows = []
for d in sorted(clean["days"]):
    info = clean["days"][d]
    day = datetime.strptime(d, "%Y-%m-%d").date()
    past = day < date.today()
    if info["type"] == "closed":
        what = "휴장"
    else:
        what = f"{info['krx'][0]} 개장 · {info['krx'][1]} 마감"
        if "nxt_pre" in info and info["nxt_pre"] is None:
            what += " · NXT 프리마켓 없음"
    tag = "" if info.get("confirmed", True) else ' <span class="tbd">예상</span>'
    rows.append(f'<tr class="{"past" if past else ""} {info["type"]}"><td>{d} ({WD[day.weekday()]})</td>'
                f'<td>{html.escape(what)}</td><td>{html.escape(info.get("note", ""))}{tag}</td></tr>')
page = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>한국 증시 장 일정 · igsignal</title>
<style>
:root{{--bg:#fff;--fg:#1d1f23;--mut:#6b707a;--line:#e5e7eb;--closed:#c62828;--special:#1565c0}}
@media (prefers-color-scheme:dark){{:root{{--bg:#14161c;--fg:#e6e6e6;--mut:#8a8f99;--line:#2a2d35;--closed:#ff6b6b;--special:#6ba8ff}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.6 system-ui,-apple-system,"Malgun Gothic",sans-serif}}
main{{max-width:720px;margin:0 auto;padding:24px 16px}}
h1{{font-size:22px;margin:0 0 4px}} p{{color:var(--mut);margin:0 0 16px}}
table{{width:100%;border-collapse:collapse}} td{{padding:8px 6px;border-bottom:1px solid var(--line)}}
tr.closed td:nth-child(2){{color:var(--closed);font-weight:600}} tr.special td:nth-child(2){{color:var(--special);font-weight:600}}
tr.past{{opacity:.45}} .tbd{{font-size:12px;border:1px solid var(--mut);border-radius:4px;padding:0 4px;color:var(--mut)}}
</style></head><body><main>
<h1>한국 증시 장 일정</h1>
<p>평일 기본 {d0[0]}~{d0[1]} (KRX 정규장). 아래는 휴장일과 거래 시간이 바뀌는 날입니다.
'예상'은 거래소 공고 전 값입니다. 갱신: {html.escape(clean.get("updated", ""))}</p>
<table>{''.join(rows)}</table>
<p style="margin-top:16px">사이드젯이 이 일정을 자동으로 받아 갑니다 · <a href="../sidejet/calendar.json">calendar.json</a></p>
</main></body></html>"""
open(os.path.join(out, "calendar", "index.html"), "w", encoding="utf-8").write(page)
open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(
    '<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=calendar/">')
print(f"OK — {out}/sidejet/calendar.json(.sig), {out}/calendar/index.html")
