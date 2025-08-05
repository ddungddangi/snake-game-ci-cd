🐍 Snake Game on Docker (3-Tier Architecture)
Flask 백엔드, HTML/JS 프론트, MySQL을 연동하여 제작한 Snake Game입니다.
Docker Compose로 전체 서비스를 컨테이너화하고, GitHub Actions로 CI/CD 파이프라인을 구성했습니다.

✅ 본 문서는 main 브랜치를 기준으로 작성되었습니다.

📁 프로젝트 구조
bash
복사
편집
├── .github/workflows/           # GitHub Actions 파이프라인 정의
│   └── docker.yml
├── templates/                   # HTML 템플릿 (Snake 게임 UI)
│   └── index.html
├── app.py                       # Flask 메인 애플리케이션 (라우팅 & 로직)
├── db.py                        # MySQL DB 연결 모듈
├── init.sql                     # DB 초기화 스크립트
├── requirements.txt             # 백엔드 의존성 정의
├── Dockerfile                   # Flask 백엔드 Dockerfile
├── docker-compose.yml           # 전체 컨테이너 정의
└── README.md                    # 프로젝트 설명
✅ 1. 주요 기술 스택
계층	기술
Frontend	HTML + JavaScript (templates/index.html)
Backend	Python Flask (app.py, db.py)
Database	MySQL (init.sql)
Infra	Docker, Docker Compose
CI/CD	GitHub Actions (docker.yml)

🐳 2. Docker 기반 로컬 실행
bash
복사
편집
docker-compose up --build
Frontend: http://localhost:5000에서 게임 실행

Backend: Flask 서버에서 점수 처리 API 제공

MySQL: 사용자 점수 저장 및 조회 처리

🔁 3. 점수 저장 API 예시
h
복사
편집
POST /score
Content-Type: application/json

{
  "username": "alice",
  "score": 180
}
🔧 4. CI/CD 구성 (GitHub Actions)
yaml
복사
편집
name: CI Build

on:
  push:
    branches: [ "main" ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build Backend Image
        run: docker build -t snake-backend -f Dockerfile .
코드 push 시 자동으로 Docker 이미지 빌드 및 테스트 수행

🧩 핵심 포인트
3계층 아키텍처로 실습 가능한 DevOps 프로젝트

Docker로 각 계층을 컨테이너화하여 독립 실행

MySQL 연동 및 초기화 스크립트 자동 적용

GitHub Actions로 자동 빌드 구성
