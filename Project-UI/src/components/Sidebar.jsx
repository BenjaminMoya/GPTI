import React from 'react';

const Sidebar = ({ history, onNewChat, onViewPlans, onLogout, onSelectChat }) => {
  return (
    <div className="sidebar">
      <button className="new-chat-btn" onClick={onNewChat}>
        + Nuevo Chat
      </button>
      <div className="chat-history">
        <ul>
          {history.map((chat) => (
            <li key={chat.id} onClick={() => onSelectChat(chat.id)}>
              {chat.title}
            </li>
          ))}
        </ul>
      </div>
      <div className="sidebar-footer">
        <div className="user-menu">
          <div onClick={onViewPlans}>✨ Actualizar a Plus</div>
          <div onClick={onLogout}>🚪 Cerrar Sesión</div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;