import React from 'react';
import './SearchBar.css';

const REGIONS = [
  { value: '', label: '🗺️ 전체 지역' },
  { value: 'seoul', label: '🏙️ 서울' },
  { value: 'busan', label: '🌊 부산' },
  { value: 'daegu', label: '🍎 대구' },
  { value: 'incheon', label: '✈️ 인천' },
  { value: 'gwangju', label: '🌸 광주' },
  { value: 'daejeon', label: '🔬 대전' },
  { value: 'ulsan', label: '🏭 울산' },
];

function SearchBar({ searchTerm, onSearchChange, region, onRegionChange }) {
  return (
    <div className="search-container">
      <select 
        id="region-select"
        value={region} 
        onChange={(e) => onRegionChange(e.target.value)}
        className="region-select"
        aria-label="지역 선택"
      >
        {REGIONS.map(r => (
          <option key={r.value} value={r.value}>{r.label}</option>
        ))}
      </select>
      
      <div className="search-input-wrapper">
        <span className="search-icon">🔍</span>
        <input
          id="search-input"
          type="text"
          placeholder="식재료 검색 (예: 사과, 돼지고기, 배추...)"
          value={searchTerm}
          onChange={(e) => onSearchChange(e.target.value)}
          className="search-input"
          aria-label="식재료 검색"
        />
        {searchTerm && (
          <button 
            id="clear-search-btn"
            className="clear-search-btn"
            onClick={() => onSearchChange('')}
            title="검색어 지우기"
            aria-label="검색어 지우기"
          >
            ✕
          </button>
        )}
      </div>
    </div>
  );
}

export default SearchBar;
