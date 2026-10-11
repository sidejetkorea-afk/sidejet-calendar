# 사이드젯 장 일정표

사이드젯이 받아 가는 **한국 증시 휴장일·거래시간 변경 일정**입니다.
배포자(sidejetkorea-afk) 한 명이 이 저장소를 관리하고, 사이드젯 사용자는 아무 설정 없이 자동으로 받습니다.

- 사이드젯이 받는 주소: `https://sidejetkorea-afk.github.io/sidejet-calendar/sidejet/calendar.json` (+ `.sig` 서명)
- 예비 주소: `https://cdn.jsdelivr.net/gh/sidejetkorea-afk/sidejet-calendar@gh-pages/sidejet/calendar.json`
- 사람이 보는 일정 페이지: `https://sidejetkorea-afk.github.io/sidejet-calendar/calendar/`

---

## 일반 사용자

- **할 일 없음.** 사이드젯을 켜 두면 켤 때와 평일 아침(07:30~08:40 중 PC마다 다른 시각)에 자동으로 받습니다.
- **서명이 확인된 일정만** 씁니다. 인터넷이 안 되면 마지막으로 받은 일정 → 프로그램에 든 기본 일정 순으로 쓰고,
  마지막에는 실제로 장이 열렸는지를 보고 바로잡습니다.
- **틀린 일정을 보면**: 사이드젯 [설정] → [장 일정] 탭 → **[일정 오류 신고]** (GitHub 로그인 필요)
  또는 이 저장소의 Issues → New issue → "일정 오류 신고".
- **급할 때**: [장 일정] 탭의 **[직접 추가…]** 로 그날을 넣으면 내 PC에서만 바로 반영됩니다 (온라인 일정보다 우선).
- 개인정보: 사이드젯은 이 파일을 받기만 하고 아무것도 보내지 않습니다. GitHub에는 일반 웹 접속 기록(IP)만 남습니다.

---

## 배포자: 처음 한 번 (약 20분)

### 준비물
- GitHub 계정 `sidejetkorea-afk` (로그인된 브라우저)
- 사이드젯이 실행되는 Windows PC (서명 키를 만들 때 씀)
- 이 저장소 파일 묶음(`sidejet-calendar.zip`)을 압축 푼 폴더

### 1단계. 저장소 만들고 파일 올리기
1. GitHub 오른쪽 위 **＋ → New repository**
2. Repository name: `sidejet-calendar` · **Public** 선택 (무료 계정의 GitHub Pages 는 공개 저장소만 됨) → **Create repository**
3. 새 저장소 화면의 **uploading an existing file** 링크를 누릅니다.
4. 압축 푼 `sidejet-calendar` 폴더를 열고, **그 안의 내용 전부**(`.github`, `tools`, `calendar.json`, `pubkeys.txt`, `README.md`)를 선택해 브라우저 창에 끌어다 놓습니다.
5. 아래 **Commit changes** 를 누릅니다.
6. 저장소 첫 화면에 `.github` 폴더가 보이는지 확인합니다. 안 보이면:
   **Add file → Create new file** → 이름 칸에 `.github/workflows/deploy.yml` 입력(슬래시를 치면 폴더가 생김) →
   압축 푼 폴더의 같은 파일 내용을 메모장으로 열어 붙여넣기 → Commit.
   `.github/workflows/weekly-check.yml`, `.github/ISSUE_TEMPLATE/calendar-error.yml` 도 같은 방법으로 만듭니다.

> 이때 Actions 탭에 빨간 ✕ 가 하나 생길 수 있습니다(아직 서명 키가 없어서). 정상이니 다음 단계로 가세요.

### 2단계. 서명 키 만들기 (사이드젯에서)
1. 사이드젯 [설정] → **[장 일정]** 탭 → 아래 **고급 설정 보기** → **[서명 키 만들기… (배포자용)]**
2. 창에 세 가지가 나옵니다. 각 칸 옆 **[복사]** 를 눌러 옮깁니다.
   - **① 현재 개인키** → GitHub 저장소 **Settings → Secrets and variables → Actions → New repository secret**
     → Name: `SIDEJET_SIGNING_KEY` · Secret: 붙여넣기 → **Add secret**
   - **② 예비 개인키** → 비밀번호 관리자·USB 등 안전한 곳에 보관 (지금은 안 씀)
   - **③ pubkeys.txt 내용** → 저장소의 `pubkeys.txt` 를 눌러 연필(✏) → 내용을 모두 지우고 붙여넣기 → **Commit changes**
3. **[sidejet.py 에 공개키 기록 (배포용)]** 을 누릅니다. 배포할 `sidejet.py` 에 공개키 2개가 기본값으로 들어갑니다
   (원본은 `sidejet.py.bak` 으로 남음).
4. 불안하면 **[텍스트 파일로 저장…]** 으로 키를 PC에 저장해 두세요. 이 창을 닫으면 개인키는 다시 볼 수 없습니다.

> 사이드젯 없이 키를 만들려면: 압축 푼 폴더에서 명령 프롬프트를 열고 `python tools\keygen.py`

### 3단계. 첫 배포
1. 저장소 **Actions** 탭 → 왼쪽 **일정표 검사·서명·배포** → 오른쪽 **Run workflow** → 초록 **Run workflow**
2. 1분쯤 기다리면 초록 ✓ 가 됩니다. 이때 저장소에 `gh-pages` 브랜치가 새로 생깁니다.

### 4단계. GitHub Pages 켜기
1. **Settings → Pages**
2. Build and deployment → Source: **Deploy from a branch**
3. Branch: **gh-pages**, 폴더: **/ (root)** → **Save**
4. 1~2분 뒤 같은 화면 위쪽에 "Your site is live at …" 가 나옵니다.

### 5단계. 확인
1. 브라우저로 `https://sidejetkorea-afk.github.io/sidejet-calendar/calendar/` → 일정 표가 보이면 성공
2. 사이드젯 [설정] → [장 일정] → **[지금 받기]** → `온라인 일정 받음 · 서명 확인됨` 이 나오면 끝

### 6단계. 계정 보호
- GitHub 계정 **2단계 인증(2FA)** 켜기 (Settings → Password and authentication)
- 다른 사람과 같이 관리한다면: Settings → Branches → `main` 보호 규칙(PR + 승인 필수)

### 7단계. 사이드젯 배포
- 2단계에서 공개키를 기록한 `sidejet.py` 를 배포합니다 (`sidejet.py.bak` 은 배포하지 않음).
- 버전을 올릴 때는 `sidejet.py` 맨 위의 `APP_VERSION` 을 바꿉니다.

---

## 배포자: 평소에 할 일

### 일정 고치기
저장소에서 `calendar.json` → 연필(✏) → `days` 에 **바뀌는 날만** 추가·수정 → **Commit changes**
→ 1~2분 뒤 자동 배포. 사이드젯은 다음 날 아침(또는 [지금 받기])에 받아 갑니다.

```json
  "2026-11-02": {"type": "closed", "note": "임시공휴일"},
  "2026-11-19": {"type": "special", "note": "수능", "krx": ["10:00", "16:30"], "nxt_pre": null, "nxt_after": ["16:30", "20:00"], "confirmed": true},
```

- 줄 끝 쉼표(`,`)에 주의하세요. **마지막 항목 뒤에는 쉼표가 없어야** 합니다.
- 틀리면 Actions 가 빨간 ✕ 로 멈추고 **이전 일정이 그대로** 유지됩니다. ✕ 를 누르면 몇 번째 줄이 틀렸는지 나옵니다.
- `updated`(작성 시각)는 배포할 때 자동으로 기록되니 적지 않아도 됩니다.

| 항목 | 뜻 |
|---|---|
| `type` | `closed` 휴장 / `special` 거래시간 변경 |
| `krx` | KRX 정규장 `["개장", "마감"]` (special 일 때 필수, 07:00~20:00) |
| `nxt_pre`, `nxt_after` | NXT 프리·애프터마켓. 운영 안 하면 `null`, 적지 않으면 평소 시간 |
| `note` | 사이드젯 화면·음성에 나오는 이름 (40자 이하) |
| `confirmed` | 공고 전 예상값이면 `false` → 사이드젯에 "예상"으로 표시. 적지 않으면 `true` |

### 공지 띄우기
`calendar.json` 맨 아래 `notice` 를 고치면 모든 사용자의 사이드젯 메인 창 위에 띠로 나옵니다.

```json
 "notice": {"text": "1.2.0 버전이 나왔습니다.", "url": "https://github.com/sidejetkorea-afk/sidejet-calendar/releases", "min_app_version": "1.2.0"}
```
- `text` 200자 이하 · `url` 은 https 주소 · `min_app_version` 보다 낮은 버전 사용자에게는 빨간 띠로 업데이트 안내
- 공지를 끝내려면 `text` 와 `min_app_version` 을 `""` 로

### 주간 점검 (자동)
매주 월요일 09:00 에 점검이 돌고, 고칠 것이 있으면 **`[점검] 일정표 확인 필요` 이슈**가 생깁니다.
- 30일 안에 '예상' 일정이 남아 있음 / 11월 15일 이후 다음 해 휴장일 미입력 / 배포 파일 서명 불일치·배포 실패
- 저장소 오른쪽 위 **Watch → All Activity** 로 해 두면 이슈가 생길 때 메일이 옵니다.
- 저장소에 60일 동안 변경이 없으면 GitHub 가 예약 작업을 멈춥니다 — 메일이 오면 Actions 탭에서 다시 켜세요.

### 1년 운영 일정
| 시기 | 할 일 |
|---|---|
| 12월 | 거래소의 다음 해 휴장일 공고 → 1년치 입력, 새해 첫 거래일 개장 시각 확인 |
| 11월 초 | 수능일 거래시간 공고 → 시간 확인 후 `"confirmed": true` |
| 수시 | 임시공휴일 발표 → 한 줄 추가, 사용자 신고 이슈 확인 |

### 키 교체 (현재 개인키가 유출됐을 때)
1. GitHub 비밀값 `SIDEJET_SIGNING_KEY` 를 **② 예비 개인키**로 바꾸고 Actions → Run workflow
   → 기존 사용자의 사이드젯도 예비 공개키를 알고 있어 그대로 받습니다.
2. 여유가 있을 때 [서명 키 만들기…]로 새 2쌍을 만들어 `pubkeys.txt`·`sidejet.py` 를 갱신하고 새 버전 배포,
   `notice.min_app_version` 으로 업데이트 안내

---

## 문제 해결

| 어디서 | 메시지 | 해결 |
|---|---|---|
| Actions | `SIDEJET_SIGNING_KEY 가 없어 서명할 수 없습니다` | 2단계 비밀값 이름(대문자·밑줄)과 값 확인 |
| Actions | `개인키가 pubkeys.txt 의 공개키와 짝이 아닙니다` | 같은 때 만든 ①과 ③인지 확인 |
| Actions | `JSON 문법 오류 N번째 줄` / `일정표 오류:` | 표시된 줄의 쉼표·따옴표·시각 형식 수정 |
| Actions | 마지막 단계 `Permission denied` / `403` | Settings → Actions → General → Workflow permissions → **Read and write** → Save 후 다시 실행 |
| Actions | 워크플로가 안 보임 | `.github/workflows/` 폴더가 올라갔는지 확인 (1단계 6번) |
| 페이지 | 404 | 4단계 Pages 설정(gh-pages / root) 확인, 1~2분 기다리기 |
| 사이드젯 | `HTTP 404` | Actions 초록 ✓ 와 4단계 확인 |
| 사이드젯 | `서명이 맞지 않음` | 비밀값 개인키와 sidejet.py 공개키가 같은 짝인지 확인 |
| 사이드젯 | `서명 공개키 미설정` | 2단계 3번 [sidejet.py 에 공개키 기록] |

메뉴 이름은 GitHub 화면이 바뀌면 조금 다를 수 있습니다.

## 파일 구성
- `calendar.json` — 일정 원본 (평소 이것만 고침)
- `pubkeys.txt` — 공개키 (배포 시 키 짝 확인, 주간 점검에 사용)
- `tools/` — 형식 검사·서명·배포 파일 생성·점검 스크립트, `keygen.py`(사이드젯 없이 키 만들 때)
- `.github/workflows/deploy.yml` — 검사 → 서명 → `gh-pages` 브랜치에 배포
- `.github/workflows/weekly-check.yml` — 주간 점검 → 이슈
- `.github/ISSUE_TEMPLATE/calendar-error.yml` — 일정 오류 신고 양식
