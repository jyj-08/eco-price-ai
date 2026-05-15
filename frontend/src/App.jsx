import { useEffect, useState } from 'react'
import axios from 'axios'

function App() {
  const [status, setStatus] = useState('서버 상태를 불러오는 중입니다...')
  const [error, setError] = useState(null)

  useEffect(() => {
    axios
      .get('http://localhost:8000')
      .then((response) => {
        setStatus(response.data?.message ?? '백엔드에 연결되었습니다.')
      })
      .catch((err) => {
        setError(err.message)
        setStatus('백엔드 연결에 실패했습니다.')
      })
  }, [])

  return (
    <div className="app-shell">
      <div className="card">
        <header className="hero">
          <p className="eyebrow">Eco-Price AI</p>
          <h1>React 프론트엔드 + Vite</h1>
          <p className="lead">
            Tailwind 스타일 감성으로 구성된 깔끔한 UI에서 백엔드 API를 호출합니다.
          </p>
        </header>

        <section className="status-card">
          <div className="status-header">
            <h2>백엔드 상태</h2>
            <span className="badge">API</span>
          </div>
          <p className="status-text">{status}</p>
          {error && <p className="error-text">오류: {error}</p>}
          <p className="hint">
            요청 URL: <code>http://localhost:8000</code>
          </p>
        </section>

        <section className="grid-panel">
          <article>
            <h3>사용 기술</h3>
            <p>Vite, React, Axios 기반의 프론트엔드 구조입니다.</p>
          </article>
          <article>
            <h3>다음 단계</h3>
            <p>추가 컴포넌트를 만들어 `/items` 또는 AI 레시피 엔드포인트 호출을 확장하세요.</p>
          </article>
        </section>
      </div>
    </div>
  )
}

export default App
