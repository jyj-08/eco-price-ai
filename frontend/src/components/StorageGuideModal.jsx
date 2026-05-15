import { useState } from 'react';
import '../styles/StorageGuideModal.css';

function StorageGuideModal({ isOpen, itemName, storageData, onClose, isLoading }) {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{itemName} - 보관 가이드</h2>
          <button className="close-btn" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="modal-body">
          {isLoading ? (
            <div className="loading">로딩 중...</div>
          ) : storageData ? (
            <div className="storage-info">
              <div className="info-section">
                <h3>💾 보관 방법</h3>
                <p>{storageData.storage_method}</p>
              </div>

              <div className="info-section">
                <h3>📅 유통기한</h3>
                <p>개봉 후 {storageData.shelf_life_days}일 이내 섭취 권장</p>
              </div>

              <div className="info-section">
                <h3>❄️ 냉동 보관</h3>
                <p>
                  {storageData.is_freezable
                    ? '✅ 냉동 보관 가능합니다'
                    : '❌ 냉동 보관은 권장하지 않습니다'}
                </p>
              </div>
            </div>
          ) : (
            <div className="error">정보를 불러올 수 없습니다</div>
          )}
        </div>

        <div className="modal-footer">
          <button className="btn-close" onClick={onClose}>
            닫기
          </button>
        </div>
      </div>
    </div>
  );
}

export default StorageGuideModal;
