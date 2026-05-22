import React from 'react';

/**
 * isCatalogMode 판별 기준:
 *  1. item.market_name 이 숫자로만 이루어진 문자열 (예: '484')
 *  2. item.price 가 10 · 100 · 250 · 500 · 1000 같은 "기준 용량" 후보 수치
 *  3. item.unit 이 영문 대문자로만 구성 (G, ML, KG, L 등)
 * 셋 중 두 가지 이상 충족하면 카탈로그 모드로 판정합니다.
 */
function detectCatalogMode(item) {
  if (!item) return false;

  // 조건 1: market_name 이 순수 숫자 문자열
  const marketIsNumeric =
    item.market_name != null &&
    /^\d+$/.test(String(item.market_name).trim());

  // 조건 2: price 가 전형적인 기준 용량 값 (≤ 5000 이하의 작은 정수)
  const typicalVolumes = [10, 50, 100, 150, 200, 250, 300, 500, 750, 1000, 1500, 2000, 5000];
  const priceIsVolume =
    item.price != null &&
    Number.isInteger(Number(item.price)) &&
    typicalVolumes.includes(Number(item.price));

  // 조건 3: unit 이 영문(알파벳)으로만 구성
  const unitIsEnglish =
    item.unit != null &&
    /^[A-Za-z]+$/.test(String(item.unit).trim());

  const score = [marketIsNumeric, priceIsVolume, unitIsEnglish].filter(Boolean).length;
  return score >= 2;
}

function PriceCard({ item, isLowest, isSelected, onToggle, onClick }) {
  const isCatalogMode = detectCatalogMode(item);

  return (
    <div
      className={`price-card ${isLowest ? 'lowest-price' : ''} ${isSelected ? 'selected' : ''}`}
      onClick={() => item?.item_name && onClick(item.item_name)}
      role="button"
      tabIndex={0}
      aria-label={`${item?.item_name} 카드 - 클릭하여 보관 가이드 확인`}
      onKeyDown={(e) => e.key === 'Enter' && item?.item_name && onClick(item.item_name)}
    >
      {/* 최저가 배지 — 가격 모드에서만 의미 있음 */}
      {!isCatalogMode && isLowest && (
        <div className="lowest-price-badge">🏆 최저가</div>
      )}

      {/* 카탈로그 모드 배지 */}
      {isCatalogMode && (
        <div className="catalog-mode-badge">📋 카탈로그</div>
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

      {/* ─── 가격 / 용량 표시 분기 ─── */}
      <div className="item-price">
        {isCatalogMode ? (
          /* 카탈로그 모드: "기준 용량: 100 G" */
          item?.price && item?.unit
            ? <span className="catalog-volume">기준 용량: {item.price} {item.unit}</span>
            : item?.price
              ? <span className="catalog-volume">기준 용량: {item.price}</span>
              : <span className="no-data">용량 정보 없음</span>
        ) : (
          /* 가격 모드: "1,234원" */
          item?.price
            ? `${Number(item.price).toLocaleString('ko-KR')}원`
            : '가격 정보 없음'
        )}
      </div>

      {/* ─── 메타 배지 분기 ─── */}
      <div className="item-meta">
        {isCatalogMode ? (
          <>
            {/* 카탈로그 모드: 상품코드 표시, unit은 위에서 이미 표시했으므로 생략 */}
            {item?.market_name && /^\d+$/.test(String(item.market_name).trim()) && (
              <span className="meta-badge meta-badge-code">
                🔖 상품코드: {item.market_name}
              </span>
            )}
            {/* region: '-' 같은 더미 값 필터링 */}
            {item?.region && item.region.trim() !== '-' && item.region.trim() !== '' && (
              <span className="meta-badge meta-badge-region">
                📍 {item.region}
              </span>
            )}
          </>
        ) : (
          <>
            {/* 가격 모드: 기존 배지 */}
            {item?.unit && item.unit.trim() !== '-' && (
              <span className="meta-badge meta-badge-unit">
                ⚖️ {item.unit}
              </span>
            )}
            {item?.market_name && item.market_name.trim() !== '-' && (
              <span className="meta-badge meta-badge-market">
                🏪 {item.market_name}
              </span>
            )}
            {item?.region && item.region.trim() !== '-' && item.region.trim() !== '' && (
              <span className="meta-badge meta-badge-region">
                📍 {item.region}
              </span>
            )}
          </>
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
