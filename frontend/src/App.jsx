import { useState, useEffect } from 'react'
import MarketPrices from './components/MarketPrices'
import { getMarketPrices, createAiRecipe } from './api'
import './App.css'

function App() {
  const [searchTerm, setSearchTerm] = useState('')
  const [prices, setPrices] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  
  // AI 레시피 관련 상태
  const [isLoading, setIsLoading] = useState(false)
  const [recipeResult, setRecipeResult] = useState(null)
  const [selectedIngredients, setSelectedIngredients] = useState([])

  // 검색어 변경 시 데이터 로드
  useEffect(() => {
    loadMarketPrices()
  }, [searchTerm])

  const loadMarketPrices = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getMarketPrices(searchTerm || null)
      setPrices(data)
    } catch (err) {
      setError('마켓 가격을 불러올 수 없습니다')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value)
  }

  // AI 레시피 생성
  const handleCreateRecipe = async () => {
    if (selectedIngredients.length === 0) {
      alert('레시피를 만들 재료를 선택해주세요!')
      return
    }

    setIsLoading(true)
    setRecipeResult(null)
    
    try {
      const result = await createAiRecipe(selectedIngredients)
      setRecipeResult(result)
    } catch (err) {
      console.error('레시피 생성 실패:', err)
      alert('레시피 생성에 실패했습니다.')
    } finally {
      setIsLoading(false)
    }
  }

  // 재료 선택/해제
  const toggleIngredient = (ingredientName) => {
    setSelectedIngredients(prev => 
      prev.includes(ingredientName)
        ? prev.filter(item => item !== ingredientName)
        : [...prev, ingredientName]
    )
  }

  return (
    <>
      <div className="app-header">
        <h1>🌱 Eco-Price AI</h1>
        <p>저가 식재료 정보와 AI 기반 레시피 서비스</p>
        
        {/* 검색 입력창 */}
        <div className="search-container">
          <input
            type="text"
            placeholder="식재료 검색 (예: 사과, 고기, 채소...)"
            value={searchTerm}
            onChange={handleSearchChange}
            className="search-input"
          />
          {searchTerm && (
            <button 
              className="clear-search-btn"
              onClick={() => setSearchTerm('')}
              title="검색어 지우기"
            >
              ✕
            </button>
          )}
        </div>
      </div>
      
      <main className="app-main">
        {/* AI 레시피 생성 섹션 */}
        <div className="recipe-section">
          <h2>🤖 AI 레시피 생성</h2>
          
          {/* 선택된 재료 표시 */}
          {selectedIngredients.length > 0 && (
            <div className="selected-ingredients">
              <h3>선택된 재료:</h3>
              <div className="ingredient-tags">
                {selectedIngredients.map(ingredient => (
                  <span key={ingredient} className="ingredient-tag">
                    {ingredient}
                    <button onClick={() => toggleIngredient(ingredient)}>×</button>
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* AI 레시피 생성 버튼 */}
          <button 
            className="btn-create-recipe"
            onClick={handleCreateRecipe}
            disabled={selectedIngredients.length === 0 || isLoading}
          >
            {isLoading ? '생성 중...' : '🍳 AI 레시피 생성'}
          </button>

          {/* 로딩 상태 표시 */}
          {isLoading && (
            <div className="recipe-loading">
              <div className="loading-spinner"></div>
              <p>AI가 가성비 레시피를 짜고 있어요... 🍳</p>
            </div>
          )}

          {/* 레시피 결과 표시 */}
          {recipeResult && !isLoading && (
            <div className="recipe-result">
              <h3>{recipeResult.title}</h3>
              <div className="recipe-info">
                <p><strong>재료:</strong> {recipeResult.main_ingredients.join(', ')}</p>
                <p><strong>예상 비용:</strong> {recipeResult.estimated_cost.toLocaleString()}원</p>
              </div>
              <div className="recipe-instructions">
                <strong>조리법:</strong>
                {typeof recipeResult.instructions === 'string' 
                  ? <p>{recipeResult.instructions}</p>
                  : Array.isArray(recipeResult.instructions)
                    ? <ol>{recipeResult.instructions.map((step, idx) => <li key={idx}>{step}</li>)}</ol>
                    : <pre>{JSON.stringify(recipeResult.instructions, null, 2)}</pre>
                }
              </div>
            </div>
          )}
        </div>

        {/* 시장 가격 섹션 */}
        <MarketPrices 
          prices={prices}
          loading={loading}
          error={error}
          onRefresh={loadMarketPrices}
          onIngredientToggle={toggleIngredient}
          selectedIngredients={selectedIngredients}
        />
      </main>
    </>
  )
}

export default App
                <img className="button-icon" src={reactLogo} alt="" />
                Learn more
              </a>
            </li>
          </ul>
        </div>
        <div id="social">
          <svg className="icon" role="presentation" aria-hidden="true">
            <use href="/icons.svg#social-icon"></use>
          </svg>
          <h2>Connect with us</h2>
          <p>Join the Vite community</p>
          <ul>
            <li>
              <a href="https://github.com/vitejs/vite" target="_blank">
                <svg
                  className="button-icon"
                  role="presentation"
                  aria-hidden="true"
                >
                  <use href="/icons.svg#github-icon"></use>
                </svg>
                GitHub
              </a>
            </li>
            <li>
              <a href="https://chat.vite.dev/" target="_blank">
                <svg
                  className="button-icon"
                  role="presentation"
                  aria-hidden="true"
                >
                  <use href="/icons.svg#discord-icon"></use>
                </svg>
                Discord
              </a>
            </li>
            <li>
              <a href="https://x.com/vite_js" target="_blank">
                <svg
                  className="button-icon"
                  role="presentation"
                  aria-hidden="true"
                >
                  <use href="/icons.svg#x-icon"></use>
                </svg>
                X.com
              </a>
            </li>
            <li>
              <a href="https://bsky.app/profile/vite.dev" target="_blank">
                <svg
                  className="button-icon"
                  role="presentation"
                  aria-hidden="true"
                >
                  <use href="/icons.svg#bluesky-icon"></use>
                </svg>
                Bluesky
              </a>
            </li>
          </ul>
        </div>
      </section>

      <div className="ticks"></div>
      <section id="spacer"></section>
    </>
  )
}

export default App
