import axios from 'axios';

// 백엔드 API 기본 인스턴스 생성
const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * 마켓 가격 데이터 조회
 * @param {string} searchTerm - 검색 키워드 (선택사항)
 * @returns {Promise} 마켓 가격 데이터 배열
 */
export const getMarketPrices = async (searchTerm = null) => {
  try {
    const params = searchTerm ? { q: searchTerm } : {};
    const response = await apiClient.get('/items', { params });
    return response.data;
  } catch (error) {
    console.error('마켓 가격 조회 실패:', error);
    throw error;
  }
};

/**
 * AI 레시피 생성
 * @param {Array<string>} ingredients - 재료 배열
 * @returns {Promise} AI 생성된 레시피 데이터
 */
export const createAiRecipe = async (ingredients) => {
  try {
    const response = await apiClient.post('/api/ai/recipe', {
      ingredients,
    });
    return response.data;
  } catch (error) {
    console.error('AI 레시피 생성 실패:', error);
    throw error;
  }
};

/**
 * 식재료 보관 가이드 조회
 * @param {string} itemName - 식재료 이름
 * @returns {Promise} 보관 가이드 데이터
 */
export const getStorageGuide = async (itemName) => {
  try {
    const response = await apiClient.get(`/api/storage/${itemName}`);
    return response.data;
  } catch (error) {
    console.error('보관 가이드 조회 실패:', error);
    throw error;
  }
};

export default apiClient;
