import React, { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import AuthService from "../../services/authService";
import AuthContext from '../../context/AuthContext';

const Login = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const { setUser } = useContext(AuthContext);

  const handleLogin = async (e) => {
    e.preventDefault();
  
    setMessage("");
    setLoading(true);
    try {
      const success = await AuthService.login(username, password);
      if (success) {
        // Set the user in the context
        const currentUser = AuthService.getCurrentUser();
        console.log(currentUser);
        setUser(currentUser);
  
        // Navigate to the dashboard
        navigate('/');
      }
    } catch (error) {
      const resMessage =
        (error.response &&
          error.response.data &&
          error.response.data.message) ||
        error.message ||
        error.toString();
  
      setLoading(false);
      setMessage(resMessage);
    }
  };

  return (
    <div>
      <form onSubmit={handleLogin}>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button disabled={loading} type="submit">
          {loading ? "Loading..." : "Login"}
        </button>
      </form>

      {message && <div>{message}</div>}
    </div>
  );
};

export default Login;
