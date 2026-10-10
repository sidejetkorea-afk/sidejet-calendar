# 사이드젯 장 일정표 (data.igsignal.com)

사이드젯이 아침마다 받아 가는 한국 증시 휴장일·거래시간 변경 일정입니다.
`calendar.json` 하나만 고치면 GitHub가 검사 → 서명 → 배포까지 자동으로 합니다.

- 사이드젯이 받는 주소: `https://data.igsignal.com/sidejet/calendar.json` (+ `.sig` 서명)
- 사람이 보는 일정 페이지: `https://data.igsignal.com/calendar/`

---

## 처음 한 번만 하는 설정 (약 15분)

### 1. 서명 키 만들기 (본인 PC에서)
```
pip install cryptography
python tools/keygen.py
```
- **개인키** → GitHub 저장소 **Settings → Secrets and variables → Actions → New repository secret**
  - 이름: `SIDEJET_SIGNING_KEY`, 값: 출력된 개인키
  - 어디에도 붙여 넣거나 공유하지 마세요. 잃어버리면 새로 만들고 사이드젯의 공개키도 바꿔야 합니다.
- **공개키** → `sidejet.py` 맨 위의 `CALENDAR_PUBKEY = "..."` 에 붙여 넣기

### 2. 저장소 만들고 올리기
1. GitHub에서 새 저장소 생성 (예: `sidejet-calendar`, 공개 저장소 가능 — 비밀 정보 없음)
2. 이 폴더의 파일을 그대로 올림 (`.github` 폴더 포함)

### 3. GitHub Pages 켜기
- 저장소 **Settings → Pages → Build and deployment → Source: GitHub Actions**
- 같은 화면 **Custom domain** 에 `data.igsignal.com` 입력 → Save
- DNS 확인이 끝나면 **Enforce HTTPS** 체크

### 4. DNS 설정 (igsignal.com 을 관리하는 곳에서)
| 종류 | 이름(호스트) | 값 |
|---|---|---|
| CNAME | `data` | `<GitHub 아이디>.github.io` |

반영까지 몇 분~몇 시간 걸릴 수 있습니다.

### 5. 확인
- 저장소 **Actions** 탭에서 "일정표 검사·서명·배포" 가 초록색인지 확인
- 브라우저로 `https://data.igsignal.com/calendar/` 접속
- 사이드젯 **[설정] → [장 일정…] → [지금 받기]** → "서명 확인됨" 이 나오면 끝

---

## 일정 고치는 법

`calendar.json` 의 `days` 에 **바뀌는 날만** 적습니다. 목록에 없는 평일은 기본 시간(`default`)입니다.

```json
"2026-12-31": {"type": "closed", "note": "연말 휴장", "confirmed": true},
"2026-11-19": {"type": "special", "note": "수능", "krx": ["10:00", "16:30"],
               "nxt_pre": null, "nxt_after": ["16:30", "20:00"], "confirmed": false}
```

| 항목 | 뜻 |
|---|---|
| `type` | `closed` 휴장 / `special` 거래시간 변경 |
| `krx` | KRX 정규장 [개장, 마감] (special 일 때 필수) |
| `nxt_pre`, `nxt_after` | NXT 프리·애프터마켓 시간, 운영 안 하면 `null` (생략하면 기본값) |
| `note` | 사이드젯 화면·음성에 나오는 이름 (40자 이하) |
| `confirmed` | 거래소 공고 전 예상값이면 `false` → 사이드젯에 "예상"으로 표시 |

GitHub 웹에서 파일을 열고 연필 버튼으로 고친 뒤 **Commit** 하면 1~2분 안에 배포됩니다.
형식이 틀리면 배포가 멈추고 Actions 탭에 이유가 나옵니다 (기존 일정은 그대로 유지).

### 1년 운영 일정
| 시기 | 할 일 |
|---|---|
| 12월 | 거래소의 다음 해 휴장일 공고 → 1년치 입력, 새해 첫 거래일 개장 시각 확인 |
| 11월 초 | 수능일 거래시간 공고 확인 → `confirmed: true` |
| 수시 | 임시공휴일 발표 → 한 줄 추가 |

## 파일 구성
- `calendar.json` — 일정 원본
- `tools/calendar_lib.py` — 형식 검사 규칙 (사이드젯과 같은 규칙)
- `tools/validate.py` — 형식 검사 (`python tools/validate.py calendar.json`)
- `tools/build_site.py` — 서명 + 배포 폴더 + 일정 페이지 생성
- `tools/keygen.py` — 서명 키 만들기 (처음 한 번)
- `.github/workflows/deploy.yml` — 자동 검사·서명·배포
