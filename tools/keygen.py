# -*- coding: utf-8 -*-
"""
서명 키 2쌍(현재·예비) 만들기 — 사이드젯 [설정] → 장 일정 → 고급 → [서명 키 만들기…] 와 같은 일을 합니다.
  python tools/keygen.py
개인키는 화면에만 보여 주고 파일로 저장하지 않습니다. 이 저장소에 개인키를 올리지 마세요.
"""
import base64
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from calendar_lib import Ed25519  # noqa: E402


def main():
    seeds = [os.urandom(32), os.urandom(32)]
    privs = [base64.b64encode(s).decode() for s in seeds]
    pubs = [base64.b64encode(Ed25519.public_key(s)).decode() for s in seeds]
    print("=" * 70)
    print("① 현재 개인키 → GitHub 저장소 Settings → Secrets and variables → Actions")
    print("   → New repository secret · Name: SIDEJET_SIGNING_KEY · Secret: 아래 값")
    print(f"   {privs[0]}")
    print()
    print("② 예비 개인키 → 비밀번호 관리자·USB 등 안전한 곳에 보관 (지금은 안 씀)")
    print(f"   {privs[1]}")
    print()
    print("③ pubkeys.txt 에 붙여넣을 내용 (공개키)")
    print("# 사이드젯 일정표 서명 공개키 (첫 줄: 현재, 둘째 줄: 예비)")
    print(pubs[0])
    print(pubs[1])
    print()
    print("④ sidejet.py 의 이 줄을 바꾸세요 (배포용)")
    print(f'CALENDAR_PUBKEYS = ["{pubs[0]}", "{pubs[1]}"]')
    print("=" * 70)


if __name__ == "__main__":
    main()
