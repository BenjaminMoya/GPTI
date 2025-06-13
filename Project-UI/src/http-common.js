import axios from "axios";

const backendServer = import.meta.env.VITE_BACKEND_SERVER;
const backendPort = import.meta.env.VITE_BACKEND_PORT;

export default axios.create({
    baseURL: `http://127.0.0.1:8000`,
    headers: {
        'Content-Type': 'application/json'
    }
});