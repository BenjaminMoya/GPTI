import React from 'react';
import styles from '../styles/LeftSidebar.module.css';
import { FiPlus, FiMessageSquare, FiMenu } from 'react-icons/fi';
import { DiGoogleCloudPlatform } from 'react-icons/di';

function LeftSidebar({ promptHistory }) {

  const handleRefresh = () => {
    window.location.reload();
  }

  return (
    <div className={styles.sidebar}>
      <div className={styles.header}>
        <FiMenu size={20} className={styles.menuIcon} />
        <div className={styles.logo}>
          <DiGoogleCloudPlatform size={26} color="#8ab4f8" onClick={handleRefresh} style={{ cursor: "pointer" }}/>
          <span onClick={handleRefresh} style={{ cursor: "pointer" }}>Cientific AI</span>
        </div>
      </div>
      
      <button onClick={handleRefresh} className={styles.newChatButton}>
        <FiPlus size={20} />
        <span>Create new</span>
      </button>

      <div className={styles.divider}></div>
      <div className={styles.recent}>
        <h3 className={styles.recentTitle}>Recent</h3>
        <ul>
          {promptHistory.map((item, index) => (
            <li key={index}>
              <FiMessageSquare size={16} />
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </div>
      <div className={styles.footer}>
        {/* Aquí podrían ir otros links como 'Get API Key', etc. */}
      </div>
    </div>
  );
}

export default LeftSidebar;