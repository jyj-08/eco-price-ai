import React from 'react';

function PriceCard({ item, isLowest, isSelected, onToggle, onClick }) {
  return (
    <div
      className={`price-card ${isLowest ? 'lowest-price' : ''} ${isSelected ? 'selected' : ''}`}
      onClick={() => item?.item_name && onClick(item.item_name)}
      role="button"
      tabIndex={0}
      aria-label={`${item?.item_name} 카드 - 클릭하여 보관 가이드 확인`}
      onKeyDown={(e) => e.key === 'Enter' && item?.item_name && onClick(item.item_name)}
    >
      {/* 최저가 배지 */}
      {isLowest && (
        <div className="lowest-price-badge">🏆 최저가</div>
      )}

      {/* 레시피 선택 체크박스 */}
      <div className="ingredient-select">
        <input
          type="checkbox"
          id={`ingredient-${item?.price_id || item?.item_name}`}
          checked={isSelected}
          onChange={(e) => {
            e.stopPropagation();
            if (item?.item_name) onToggle(item.item_name);
          }}
          onClick={(e) => e.stopPropagation()}
          aria-label={`${item?.item_name} 레시피용 선택`}
        />
        <label 
          htmlFor={`ingredient-${item?.price_id || item?.item_name}`}
          onClick={(e) => e.stopPropagation()}
        >
          레시피용 선택
        </label>
      </div>

      {/* 식재료 이름 */}
      <div className="item-name">
        {item?.item_name || '이름 없음'}
      </div>

      {/* 가격 */}
      <div className="item-price">
        {item?.price ? `${item.price.toLocaleString('ko-KR')}원` : '가격 정보 없음'}
      </div>

      {/* 메타 배지들 */}
      <div className="item-meta">
        {item?.unit && (
          <span className="meta-badge meta-badge-unit">
            ⚖️ {item.unit}
          </span>
        )}
        {item?.market_name && (
          <span className="meta-badge meta-badge-market">
            🏪 {item.market_name}
          </span>
        )}
        {item?.region && (
          <span className="meta-badge meta-badge-region">
            📍 {item.region}
          </span>
        )}
      </div>

      {/* 보관 가이드 버튼 */}
      <button
        className="btn-storage-guide"
        onClick={(e) => {
          e.stopPropagation();
          if (item?.item_name) onClick(item.item_name);
        }}
        aria-label={`${item?.item_name} 보관 가이드 보기`}
      >
        📦 보관 가이드 보기
      </button>
    </div>
  );
}

export default PriceCard;
