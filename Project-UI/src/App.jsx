import './App.css'
import {HashRouter as Router, Route, Routes} from 'react-router-dom'
import Login from './components/Login';
import Chat from './components/ChatView'

function App() {
  return (
      <Router>
          <div className="container">
            <Routes>
              <Route path="/" element={<Login/>} />
              <Route path="/chat" element={<Chat/>} />
            </Routes>
          </div>
      </Router>
  );
}

export default App