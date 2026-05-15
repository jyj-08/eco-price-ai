import React from 'react';

function PriceCard({ item, isLowest, isSelected, onToggle, onClick }) {
  return (
    <div
      className={`price-card ${isLowest ? 'lowest-price' : ''} ${isSelected ? 'selected' : ''}`}
      onClick={() => onClick(item.item_name)}
    >
      {isLowest && (
        <div className="lowest-price-badge">🏆 최저가</div>
      )}

      <div className="ingredient-select">
        <input
          type="checkbox"
          checked={isSelected}
          onChange={(e) => {
            e.stopPropagation();
            onToggle(item.item_name);
          }}
          onClick={(e) => e.stopPropagation()}
        />
        <label>레시피용 선택</label>
      </div>

      <div className="item-name">{item.item_name}</div>
      <div className="item-price">{item.price?.toLocaleString('ko-KR')}원</div>
      <div className="item-unit">{item.unit || '-'}</div>
      <div className="item-market">{item.market_name || '-'}</div>
      <div className="item-region">{item.region || '-'}</div>
      <div className="click-hint">👆 클릭하여 보관법 확인</div>
    </div>
  );
}

export default PriceCard;
