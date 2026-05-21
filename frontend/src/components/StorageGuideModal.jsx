import '../styles/StorageGuideModal.css';

// 식재료 이름에 맞는 이모지 반환
function getItemEmoji(name) {
  if (!name) return '🥬';
  const n = name.toLowerCase();
  if (n.includes('사과') || n.includes('apple')) return '🍎';
  if (n.includes('배') && !n.includes('배추')) return '🍐';
  if (n.includes('바나나')) return '🍌';
  if (n.includes('딸기')) return '🍓';
  if (n.includes('포도')) return '🍇';
  if (n.includes('귤') || n.includes('오렌지')) return '🍊';
  if (n.includes('복숭아')) return '🍑';
  if (n.includes('토마토')) return '🍅';
  if (n.includes('당근')) return '🥕';
  if (n.includes('양파')) return '🧅';
  if (n.includes('마늘')) return '🧄';
  if (n.includes('배추') || n.includes('양배추')) return '🥬';
  if (n.includes('감자')) return '🥔';
  if (n.includes('고구마')) return '🍠';
  if (n.includes('옥수수')) return '🌽';
  if (n.includes('버섯')) return '🍄';
  if (n.includes('브로콜리')) return '🥦';
  if (n.includes('계란') || n.includes('달걀')) return '🥚';
  if (n.includes('닭') || n.includes('chicken')) return '🍗';
  if (n.includes('돼지') || n.includes('삼겹')) return '🥩';
  if (n.includes('소') || n.includes('쇠') || n.includes('beef')) return '🥩';
  if (n.includes('생선') || n.includes('고등어') || n.includes('연어') || n.includes('참치')) return '🐟';
  if (n.includes('새우')) return '🦐';
  if (n.includes('두부')) return '🫘';
  if (n.includes('쌀') || n.includes('밥')) return '🍚';
  if (n.includes('면') || n.includes('라면')) return '🍜';
  return '🥬';
}

function StorageGuideModal({ isOpen, itemName, storageData, onClose, isLoading }) {
  if (!isOpen) return null;

  const emoji = getItemEmoji(itemName);

  return (
    <div
      className="modal-overlay"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label={`${itemName} 보관 가이드`}
    >
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>

        {/* ===== Header ===== */}
        <div className="modal-header">
          <span className="modal-item-emoji">{emoji}</span>
          <div className="modal-header-text">
            <p className="modal-header-label">보관 가이드</p>
            <h2>{itemName}</h2>
            <p className="modal-header-sub">올바른 보관법으로 신선도를 유지하세요</p>
          </div>
          <button
            id="modal-close-btn"
            className="close-btn"
            onClick={onClose}
            aria-label="모달 닫기"
          >
            ✕
          </button>
        </div>

        {/* ===== Body ===== */}
        <div className="modal-body">
          {isLoading ? (
            <div className="modal-loading">
              <div className="spinner"></div>
              <p>보관 정보를 불러오는 중...</p>
            </div>
          ) : storageData ? (
            <div className="storage-info">

              {/* 보관 방법 */}
              <div className="info-card">
                <div className="info-card-icon green">💡</div>
                <div className="info-card-content">
                  <p className="info-card-label">보관 방법</p>
                  <p className="info-card-value">{storageData.storage_method}</p>
                </div>
              </div>

              {/* 유통기한 */}
              <div className="info-card">
                <div className="info-card-icon blue">📅</div>
                <div className="info-card-content">
                  <p className="info-card-label">권장 소비 기한</p>
                  <p className="info-card-value">
                    개봉 후 <strong>{storageData.shelf_life_days}일</strong> 이내 섭취 권장
                  </p>
                </div>
              </div>

              {/* 냉동 보관 여부 */}
              <div className="info-card">
                <div className="info-card-icon purple">🧊</div>
                <div className="info-card-content">
                  <p className="info-card-label">냉동 보관</p>
                  <span className={`freezable-badge ${storageData.is_freezable ? 'yes' : 'no'}`}>
                    {storageData.is_freezable ? '✅ 냉동 보관 가능' : '❌ 냉동 보관 불가'}
                  </span>
                </div>
              </div>

            </div>
          ) : (
            <div className="modal-error">
              <div className="modal-error-icon">🔍</div>
              <p>보관 정보를 불러올 수 없습니다.</p>
            </div>
          )}
        </div>

        {/* ===== Footer ===== */}
        <div className="modal-footer">
          <button
            id="modal-confirm-close-btn"
            className="btn-modal-close"
            onClick={onClose}
          >
            ✓ 확인했어요
          </button>
        </div>
      </div>
    </div>
  );
}

export default StorageGuideModal;
