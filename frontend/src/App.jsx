import { useState, useEffect } from 'react'
import MarketPrices from './components/MarketPrices'
import SearchBar from './components/SearchBar'
import { getMarketPrices, createAiRecipe } from './api'
import './App.css'

function App() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedRegion, setSelectedRegion] = useState('')
  const [prices, setPrices] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  
  // AI 레시피 관련 상태
  const [isLoading, setIsLoading] = useState(false)
  const [recipeResult, setRecipeResult] = useState(null)
  const [selectedIngredients, setSelectedIngredients] = useState([])

  // 검색어 또는 지역 변경 시 데이터 로드
  useEffect(() => {
    loadMarketPrices()
  }, [searchTerm, selectedRegion])

  const loadMarketPrices = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getMarketPrices(searchTerm || null, selectedRegion || null)
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
      {/* ===== Header ===== */}
      <header className="app-header">
        <div className="header-content">
          <div className="header-badge">
            <span>🌿</span>
            <span>친환경 스마트 장보기 서비스</span>
          </div>
          <h1>
            <span className="header-title-em">Eco</span>-Price <span className="header-title-em">AI</span>
          </h1>
          <p className="header-subtitle">저가 식재료 가격 비교 &amp; AI 맞춤 레시피</p>

          {/* 검색 및 지역 선택 컴포넌트 */}
          <div className="header-search-wrap">
            <SearchBar
              searchTerm={searchTerm}
              onSearchChange={setSearchTerm}
              region={selectedRegion}
              onRegionChange={setSelectedRegion}
            />
          </div>
        </div>
      </header>
      
      <main className="app-main">
        {/* ===== AI 레시피 생성 섹션 ===== */}
        <div className="recipe-section">
          <div className="recipe-section-header">
            <div className="recipe-section-icon">🤖</div>
            <h2>AI 레시피 생성</h2>
          </div>
          
          {/* 선택된 재료 표시 */}
          {selectedIngredients.length > 0 && (
            <div className="selected-ingredients">
              <h3>선택된 재료</h3>
              <div className="ingredient-tags">
                {selectedIngredients.map(ingredient => (
                  <span key={ingredient} className="ingredient-tag">
                    🥬 {ingredient}
                    <button onClick={() => toggleIngredient(ingredient)} aria-label={`${ingredient} 제거`}>×</button>
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* AI 레시피 생성 버튼 */}
          <button 
            id="btn-create-recipe"
            className="btn-create-recipe"
            onClick={handleCreateRecipe}
            disabled={selectedIngredients.length === 0 || isLoading}
          >
            {isLoading
              ? <><span className="spinner spinner-sm"></span><span>생성 중...</span></>
              : <><span>🍳</span><span>AI 레시피 생성하기</span></>
            }
          </button>

          {/* 로딩 상태 표시 */}
          {isLoading && (
            <div className="recipe-loading">
              <div className="spinner"></div>
              <p>AI가 가성비 레시피를 짜고 있어요... 🍳</p>
            </div>
          )}

          {/* 레시피 결과 표시 */}
          {recipeResult && !isLoading && (
            <div className="recipe-result">
              <div className="recipe-result-header">
                <h3>{recipeResult.title}</h3>
                <div className="recipe-meta">
                  <span className="recipe-meta-item">
                    🥘 {recipeResult.main_ingredients?.join(', ')}
                  </span>
                  <span className="recipe-meta-item">
                    💰 예상 비용: {recipeResult.estimated_cost?.toLocaleString()}원
                  </span>
                </div>
              </div>
              <div className="recipe-result-body">
                <div className="recipe-instructions">
                  <strong>📋 조리법</strong>
                  {typeof recipeResult.instructions === 'string' 
                    ? <p>{recipeResult.instructions}</p>
                    : Array.isArray(recipeResult.instructions)
                      ? <ol>{recipeResult.instructions.map((step, idx) => <li key={idx}>{step}</li>)}</ol>
                      : <pre>{JSON.stringify(recipeResult.instructions, null, 2)}</pre>
                  }
                </div>
              </div>
            </div>
          )}
        </div>

        {/* ===== 시장 가격 섹션 ===== */}
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
