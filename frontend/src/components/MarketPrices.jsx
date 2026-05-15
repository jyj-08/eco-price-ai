import { useState } from 'react';
import { getStorageGuide } from '../api';
import StorageGuideModal from './StorageGuideModal';
import PriceCard from './PriceCard';
import '../styles/MarketPrices.css';

function MarketPrices({ prices, loading, error, onRefresh, onIngredientToggle, selectedIngredients }) {
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [storageData, setStorageData] = useState(null);
  const [storageLoading, setStorageLoading] = useState(false);

  // 최저가 항목 찾기
  const findLowestPriceItem = () => {
    if (!prices || prices.length === 0) return null;
    
    let lowestPriceItem = prices[0];
    for (const item of prices) {
      if (item.price < lowestPriceItem.price) {
        lowestPriceItem = item;
      }
    }
    return lowestPriceItem;
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

  if (loading) {
    return <div className="market-container">로딩 중...</div>;
  }

  if (error) {
    return <div className="market-container error">{error}</div>;
  }

  return (
    <div className="market-container">
      <h2>🛒 시장 가격</h2>
      <button className="btn-refresh" onClick={onRefresh}>
        새로고침
      </button>

      {prices.length === 0 ? (
        <p className="no-data">데이터가 없습니다</p>
      ) : (
        <div className="price-grid">
          {prices.map((item) => {
            const isLowestPrice = lowestPriceItem && item.price_id === lowestPriceItem.price_id;
            const isSelected = selectedIngredients.includes(item.item_name);
            return (
              <PriceCard
                key={item.price_id}
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
