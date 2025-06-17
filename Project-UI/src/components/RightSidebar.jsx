import React, { useState } from 'react';
import styles from '../styles/RightSidebar.module.css';
import { FiChevronDown } from 'react-icons/fi';

function RightSidebar() {
  const [temperature, setTemperature] = useState(0.9);
  const [isLanguageOpen, setIsLanguageOpen] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState(JSON.parse(sessionStorage.getItem('lenguage')) || 'English');

  const languages = ['English', 'Spanish', 'German', 'French', 'Portuguese'];

  const toggleAccordion = () => {
    setIsLanguageOpen(prev => !prev);
  };

  const handleSelectLanguage = (lang) => {
    setSelectedLanguage(lang);
    setIsLanguageOpen(false);
    sessionStorage.setItem('lenguage', JSON.stringify(lang));
    window.location.reload(); 
  };

  return (
    <div className={styles.sidebar}>
    
      <div className={styles.section}>
        <h3 className={styles.title}>Run settings</h3>
        <div className={styles.setting}>
          <label htmlFor="temp">Temperature</label>
          <div className={styles.sliderContainer}>
            <input 
              type="range" 
              id="temp" 
              min="0" 
              max="1" 
              step="0.1" 
              value={temperature}
              onChange={(e) => setTemperature(e.target.value)}
            />
            <span>{temperature}</span>
          </div>
        </div>
      </div>

      <div className={styles.section}>
        <h3 className={styles.title}>Language Settings</h3>
        <button className={styles.safetyButton} onClick={toggleAccordion}>
          {selectedLanguage} <FiChevronDown style={{ marginLeft: '8px' }} />
        </button>

        {isLanguageOpen && (
          <ul className={styles.languageList}>
            {languages.map((lang) => (
              <li 
                key={lang} 
                onClick={() => handleSelectLanguage(lang)}
                className={styles.languageItem}
              >
                {lang}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default RightSidebar;
