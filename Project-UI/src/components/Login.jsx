import React from 'react';
import { useNavigate } from "react-router-dom";

const Login = () => {

  const navigate = useNavigate();

  const handleLogin = () => {
    navigate("/chat");
  }

  return (
    <div className="auth-container">
      <div className="auth-box">
        <h1>Bienvenido a Cientific-IA</h1>
        <p>Inicia sesión para continuar</p>
        <input type="email" placeholder="Correo electrónico" />
        <input type="password" placeholder="Contraseña" />
        <button onClick={handleLogin}>Iniciar Sesión</button>
      </div>
    </div>
  );
};

export default Login;