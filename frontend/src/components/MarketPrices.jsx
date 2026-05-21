import { useState } from 'react';
import { getStorageGuide } from '../api';
import StorageGuideModal from './StorageGuideModal';
import PriceCard from './PriceCard';
import '../styles/MarketPrices.css';

// ===== Skeleton Card Component =====
function SkeletonCard() {
  return (
    <div className="skeleton-card">
      <div className="skeleton-line skeleton-checkbox"></div>
      <div className="skeleton-line skeleton-title"></div>
      <div className="skeleton-line skeleton-price"></div>
      <div className="skeleton-badges">
        <div className="skeleton-line skeleton-badge"></div>
        <div className="skeleton-line skeleton-badge"></div>
        <div className="skeleton-line skeleton-badge"></div>
      </div>
      <div className="skeleton-line skeleton-btn"></div>
    </div>
  );
}

function MarketPrices({ prices, loading, error, onRefresh, onIngredientToggle, selectedIngredients }) {
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [storageData, setStorageData] = useState(null);
  const [storageLoading, setStorageLoading] = useState(false);

  // 최저가 항목 찾기
  const findLowestPriceItem = () => {
    if (!prices || prices.length === 0) return null;
    let lowestPriceItem = null;
    for (const item of prices) {
      if (!item || typeof item.price !== 'number') continue;
      if (!lowestPriceItem || item.price < lowestPriceItem.price) {
        lowestPriceItem = item;
      }
    }
    return lowestPriceItem || prices[0];
  };

  const lowestPriceItem = findLowestPriceItem();

  // 아이템 클릭 시 보관 가이드 조회
  const handleItemClick = async (itemName) => {
    setSelectedItem(itemName);
    setModalOpen(true);
    setStorageLoading(true);
    setStorageData(null);

    try {
      const data = await getStorageGuide(itemName);
      setStorageData(data);
    } catch (err) {
      console.error('보관 가이드 조회 실패:', err);
      setStorageData(null);
    } finally {
      setStorageLoading(false);
    }
  };

  const closeModal = () => {
    setModalOpen(false);
    setSelectedItem(null);
    setStorageData(null);
  };

  // ===== Loading: Skeleton UI =====
  if (loading) {
    return (
      <div className="market-container">
        <div className="market-section-header">
          <div className="market-section-title">
            <div className="market-section-icon">🛒</div>
            <h2>시장 가격</h2>
          </div>
        </div>
        <div className="skeleton-grid">
          {Array.from({ length: 6 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      </div>
    );
  }

  // ===== Error State =====
  if (error) {
    return (
      <div className="market-container error-state">
        <div className="error-icon">⚠️</div>
        <h3>데이터를 불러오지 못했습니다</h3>
        <p>{error}</p>
        <button className="btn-refresh" onClick={onRefresh} style={{ marginTop: '1.5rem' }}>
          🔄 다시 시도
        </button>
      </div>
    );
  }

  return (
    <div className="market-container">
      {/* Section Header */}
      <div className="market-section-header">
        <div className="market-section-title">
          <div className="market-section-icon">🛒</div>
          <h2>
            시장 가격
            {prices.length > 0 && (
              <span className="market-count-badge">{prices.length}개</span>
            )}
          </h2>
        </div>
        <button id="btn-refresh" className="btn-refresh" onClick={onRefresh}>
          🔄 새로고침
        </button>
      </div>

      {/* Empty State */}
      {prices.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">🥦</div>
          <h3>해당하는 식자재를 찾을 수 없습니다</h3>
          <p>다른 검색어나 지역으로 다시 시도해 보세요.</p>
        </div>
      ) : (
        <div className="price-grid">
          {prices?.map((item, index) => {
            if (!item) return null;
            const isLowestPrice = lowestPriceItem && item.price_id === lowestPriceItem.price_id;
            const isSelected = selectedIngredients?.includes(item.item_name);
            return (
              <PriceCard
                key={item.price_id || index}
                item={item}
                isLowest={isLowestPrice}
                isSelected={isSelected}
                onToggle={onIngredientToggle}
                onClick={handleItemClick}
              />
            );
          })}
        </div>
      )}

      <StorageGuideModal
        isOpen={modalOpen}
        itemName={selectedItem}
        storageData={storageData}
        isLoading={storageLoading}
        onClose={closeModal}
      />
    </div>
  );
}

export default MarketPrices;
