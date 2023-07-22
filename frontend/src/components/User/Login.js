import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import AuthService from "../../services/authService";

const Login = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
  
    setMessage("");
    setLoading(true);
    try {
      const success = await AuthService.login(username, password);
      if (success) {
        // Redirect to a different page
        navigate("/");
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
