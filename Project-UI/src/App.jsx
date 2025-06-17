import React, {useState,useEffect}from 'react';
import LeftSidebar from './components/LeftSideBar';
import MainPanel from './components/MainPanel';
import RightSidebar from './components/RightSidebar';
import styles from './styles/App.module.css';

function App() {
  const [promptHistory, setPromptHistory] = useState(JSON.parse(localStorage.getItem('recentItems')));

  useEffect(() => {
    const storedHistory = JSON.parse(localStorage.getItem('recentItems'));
    setPromptHistory(storedHistory);
  }, []);

  useEffect(() => {
    localStorage.setItem('recentItems', JSON.stringify(promptHistory));
  }, [promptHistory]);

  return (
    <div className={styles.appContainer}>
      <LeftSidebar promptHistory={promptHistory}/>
      <MainPanel promptHistory={promptHistory} setPromptHistory={setPromptHistory}/>
      <RightSidebar />
    </div>
  );
}

export default App;