# -*- coding: utf-8 -*-
"""
사이드젯 일정표 공용 코드 — 형식 검사와 Ed25519 서명 (외부 라이브러리 불필요)
※ 사이드젯(sidejet.py) 안의 같은 이름 함수와 규칙이 같아야 합니다.
"""
import re
import json
from datetime import datetime

CALENDAR_SCHEMA = 1
# 평소 거래시간 (온라인 일정표의 default 가 있으면 그것을 씀)
BUILTIN_DEFAULT = {"krx": ("09:00", "15:30"), "nxt_pre": ("08:00", "08:50"), "nxt_after": ("15:30", "20:00")}
_TIME_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
_VER_RE = re.compile(r"^\d+(\.\d+){0,3}$")


def _hm(text):
    h, m = str(text).split(":")
    return int(h) * 60 + int(m)


def _fmt_hm(minutes):
    minutes = int(minutes)
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def _time_pair(v, lo="07:00", hi="21:00"):
    """["HH:MM","HH:MM"] 검사. 반환: (a, b) 또는 오류 문자열"""
    if not isinstance(v, (list, tuple)) or len(v) != 2 or not all(isinstance(x, str) for x in v):
        return "시각은 [\"HH:MM\", \"HH:MM\"] 형식이어야 합니다"
    a, b = v
    if not _TIME_RE.match(a) or not _TIME_RE.match(b):
        return f"시각 형식 오류: {a}, {b}"
    if not (_hm(lo) <= _hm(a) < _hm(b) <= _hm(hi)):
        return f"시각 범위 오류: {a}~{b} (허용 {lo}~{hi}, 시작 < 끝)"
    return (a, b)


def validate_calendar(obj, allow_normal=False):
    """
    일정표 검사. 반환: (정리된 일정, 오류 목록, 경고 목록)
    - 형식 자체가 틀리면 정리된 일정은 None
    - 날짜 항목 하나가 틀리면 그 날짜만 빼고 나머지는 씀 (오류 목록에 남김)
    ※ 사이드젯(sidejet.py) 안의 validate_calendar 와 같은 규칙
    """
    errors, warns = [], []
    if not isinstance(obj, dict):
        return None, ["일정표가 JSON 객체({ … })가 아닙니다"], warns
    schema = obj.get("schema")
    if schema != CALENDAR_SCHEMA:
        return None, [f"지원하지 않는 형식 schema={schema!r} (사이드젯 업데이트가 필요할 수 있음)"], warns
    clean = {"schema": CALENDAR_SCHEMA, "updated": str(obj.get("updated", "")),
             "default": dict(BUILTIN_DEFAULT), "days": {}, "notice": {"text": "", "url": "", "min_app_version": ""}}
    dflt = obj.get("default")
    if dflt is not None:
        if not isinstance(dflt, dict):
            errors.append("default 는 { … } 형식이어야 합니다")
        else:
            for k in ("krx", "nxt_pre", "nxt_after"):
                if k in dflt:
                    r = _time_pair(dflt[k], *(("07:00", "20:00") if k == "krx" else ("07:00", "21:00")))
                    if isinstance(r, str):
                        errors.append(f"default.{k}: {r}")
                    else:
                        clean["default"][k] = r
    days = obj.get("days", {})
    if not isinstance(days, dict):
        return None, errors + ["days 는 { \"YYYY-MM-DD\": { … } } 형식이어야 합니다"], warns
    types = ("closed", "special", "normal") if allow_normal else ("closed", "special")
    for key, e in days.items():
        try:
            datetime.strptime(key, "%Y-%m-%d")
        except (ValueError, TypeError):
            errors.append(f"{key}: 날짜는 YYYY-MM-DD 형식이어야 합니다")
            continue
        if not isinstance(e, dict):
            errors.append(f"{key}: {{ … }} 형식이어야 합니다")
            continue
        t = e.get("type")
        if t not in types:
            errors.append(f"{key}: type 은 {' / '.join(types)} 중 하나여야 합니다 (지금: {t!r})")
            continue
        item = {"type": t, "note": "", "confirmed": True}
        note = e.get("note", "")
        if not isinstance(note, str):
            errors.append(f"{key}: note 는 글자여야 합니다")
            continue
        if len(note) > 40:
            warns.append(f"{key}: note 가 40자를 넘어 잘랐습니다")
            note = note[:40]
        item["note"] = note.strip()
        conf = e.get("confirmed", True)
        if not isinstance(conf, bool):
            errors.append(f"{key}: confirmed 는 true / false 여야 합니다")
            continue
        item["confirmed"] = conf
        bad = False
        if t == "special":
            r = _time_pair(e.get("krx"), "07:00", "20:00")
            if isinstance(r, str):
                errors.append(f"{key}: krx {r}")
                continue
            item["krx"] = r
            for k in ("nxt_pre", "nxt_after"):
                if k not in e:
                    item[k] = "default"
                elif e[k] is None:
                    item[k] = None
                else:
                    r = _time_pair(e[k])
                    if isinstance(r, str):
                        errors.append(f"{key}: {k} {r}")
                        bad = True
                        break
                    item[k] = r
        if bad:
            continue
        unknown = set(e) - {"type", "note", "confirmed", "krx", "nxt_pre", "nxt_after"}
        if unknown:
            warns.append(f"{key}: 모르는 항목 무시 — {', '.join(sorted(unknown))}")
        clean["days"][key] = item
    notice = obj.get("notice")
    if notice is not None:
        if not isinstance(notice, dict):
            errors.append("notice 는 { … } 형식이어야 합니다")
        else:
            text, url, mv = notice.get("text", ""), notice.get("url", ""), notice.get("min_app_version", "")
            if not isinstance(text, str) or len(text) > 200:
                errors.append("notice.text 는 200자 이하 글자여야 합니다")
            elif not isinstance(url, str) or (url and not url.startswith("https://")):
                errors.append("notice.url 은 https:// 로 시작해야 합니다")
            elif not isinstance(mv, str) or (mv and not _VER_RE.match(mv)):
                errors.append("notice.min_app_version 은 1.2.0 같은 형식이어야 합니다")
            else:
                clean["notice"] = {"text": text.strip(), "url": url, "min_app_version": mv}
    return clean, errors, warns


# ----- Ed25519 서명 확인 (RFC 8032 기준 구현, 외부 라이브러리 불필요) -----
class Ed25519:
    p = 2 ** 255 - 19
    L = 2 ** 252 + 27742317777372353535851937790883648493
    d = -121665 * pow(121666, 2 ** 255 - 19 - 2, 2 ** 255 - 19) % (2 ** 255 - 19)
    I = pow(2, (2 ** 255 - 19 - 1) // 4, 2 ** 255 - 19)

    @classmethod
    def _add(cls, P, Q):
        p, d = cls.p, cls.d
        A = (P[1] - P[0]) * (Q[1] - Q[0]) % p
        B = (P[1] + P[0]) * (Q[1] + Q[0]) % p
        C = 2 * P[3] * Q[3] * d % p
        D = 2 * P[2] * Q[2] % p
        E, F, G, H = B - A, D - C, D + C, B + A
        return (E * F % p, G * H % p, F * G % p, E * H % p)

    @classmethod
    def _mul(cls, s, P):
        Q = (0, 1, 1, 0)
        while s > 0:
            if s & 1:
                Q = cls._add(Q, P)
            P = cls._add(P, P)
            s >>= 1
        return Q

    @classmethod
    def _equal(cls, P, Q):
        p = cls.p
        return (P[0] * Q[2] - Q[0] * P[2]) % p == 0 and (P[1] * Q[2] - Q[1] * P[2]) % p == 0

    @classmethod
    def _recover_x(cls, y, sign):
        p, d = cls.p, cls.d
        if y >= p:
            return None
        x2 = (y * y - 1) * pow(d * y * y + 1, p - 2, p)
        if x2 % p == 0:
            return None if sign else 0
        x = pow(x2, (p + 3) // 8, p)
        if (x * x - x2) % p != 0:
            x = x * cls.I % p
        if (x * x - x2) % p != 0:
            return None
        if (x & 1) != sign:
            x = p - x
        return x

    @classmethod
    def _base(cls):
        p = cls.p
        gy = 4 * pow(5, p - 2, p) % p
        gx = cls._recover_x(gy, 0)
        return (gx, gy, 1, gx * gy % p)

    @classmethod
    def _compress(cls, P):
        p = cls.p
        zinv = pow(P[2], p - 2, p)
        x, y = P[0] * zinv % p, P[1] * zinv % p
        return int.to_bytes(y | ((x & 1) << 255), 32, "little")

    @classmethod
    def _decompress(cls, s):
        if len(s) != 32:
            return None
        y = int.from_bytes(s, "little")
        sign = y >> 255
        y &= (1 << 255) - 1
        x = cls._recover_x(y, sign)
        return None if x is None else (x, y, 1, x * y % cls.p)

    @classmethod
    def _hint(cls, b):
        import hashlib
        return int.from_bytes(hashlib.sha512(b).digest(), "little") % cls.L

    @classmethod
    def _expand(cls, seed):
        import hashlib
        h = hashlib.sha512(seed).digest()
        a = int.from_bytes(h[:32], "little")
        a &= (1 << 254) - 8
        a |= 1 << 254
        return a, h[32:]

    @classmethod
    def public_key(cls, seed):
        a, _ = cls._expand(seed)
        return cls._compress(cls._mul(a, cls._base()))

    @classmethod
    def sign(cls, seed, msg):
        a, prefix = cls._expand(seed)
        G = cls._base()
        A = cls._compress(cls._mul(a, G))
        r = cls._hint(prefix + msg)
        Rs = cls._compress(cls._mul(r, G))
        s = (r + cls._hint(Rs + A + msg) * a) % cls.L
        return Rs + int.to_bytes(s, 32, "little")

    @classmethod
    def verify(cls, public, msg, sig):
        try:
            if len(public) != 32 or len(sig) != 64:
                return False
            A = cls._decompress(public)
            R = cls._decompress(sig[:32])
            if A is None or R is None:
                return False
            s = int.from_bytes(sig[32:], "little")
            if s >= cls.L:
                return False
            h = cls._hint(sig[:32] + public + msg)
            return cls._equal(cls._mul(s, cls._base()), cls._add(R, cls._mul(h, A)))
        except Exception:
            return False


def _b64decode(text, size):
    import base64
    try:
        raw = base64.b64decode(str(text).strip(), validate=True)
    except Exception:
        return None
    return raw if len(raw) == size else None


def verify_calendar_signature(raw, sig_text, pubkeys):
    """반환: 맞는 공개키 번호(0부터) 또는 None"""
    sig = _b64decode(sig_text, 64)
    if sig is None:
        return None
    for i, pk in enumerate(pubkeys):
        pub = _b64decode(pk, 32)
        if pub is not None and Ed25519.verify(pub, raw, sig):
            return i
    return None



def read_pubkeys(path):
    """pubkeys.txt: 한 줄에 공개키 하나, # 으로 시작하는 줄은 설명"""
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except OSError:
        return []
    return [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")]
