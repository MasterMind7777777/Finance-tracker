import axios from 'axios';

const API_URL = "http://localhost:8000/api_v1";

class AuthService {
  async login(username, password) {
    const response = await axios.post(API_URL + "/users/login/", {
      username,
      password
    });
    console.log(response);
    if (response.data.access_token) {
      localStorage.setItem("user", JSON.stringify(response.data));
      localStorage.setItem("user_id", JSON.stringify(response.data.user_id));
      return true; // Login successful
    }
    
    return false; // Login failed
  }

  logout() {
    localStorage.removeItem("user");
  }

  getCurrentUserId() {
    return JSON.parse(localStorage.getItem('user_id'));
  }

  getCurrentUser() {
    return JSON.parse(localStorage.getItem('user'));
  }
}

const authService = new AuthService();
export default authService;
