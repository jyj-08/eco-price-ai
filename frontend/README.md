# Eco-Price AI Frontend

이 디렉토리는 Vite와 React를 사용한 프론트엔드 앱입니다.

## 시작하기

1. `frontend` 디렉토리로 이동합니다.
2. `npm install`을 실행합니다.
3. `npm run dev`로 개발 서버를 시작합니다.

## Axios 설치

이 프로젝트는 `axios`를 이미 `package.json`에 포함하고 있습니다.
따라서 `frontend`에서 `npm install`을 실행하면 `axios`도 함께 설치됩니다.

추가로 `axios`만 별도 설치하려면:

```bash
npm install axios
```

## API 엔드포인트

- 백엔드: `http://localhost:8000`

현재 `src/App.jsx`는 루트 경로를 호출하여 백엔드 연결 상태를 확인합니다.
