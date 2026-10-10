# -*- coding: utf-8 -*-
"""서명 키 한 쌍 만들기 (처음 한 번만, 본인 PC에서 실행)
  - 개인키: GitHub 저장소 Settings → Secrets → Actions 에 SIDEJET_SIGNING_KEY 로 저장 (절대 공개 금지)
  - 공개키: sidejet.py 의 CALENDAR_PUBKEY 에 붙여 넣기
"""
import base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

key = Ed25519PrivateKey.generate()
priv = key.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw, serialization.NoEncryption())
pub = key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
print("개인키 (GitHub Secret SIDEJET_SIGNING_KEY):")
print(base64.b64encode(priv).decode())
print()
print("공개키 (sidejet.py CALENDAR_PUBKEY):")
print(base64.b64encode(pub).decode())
