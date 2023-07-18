import instance from './index.js';
import AuthService from '../services/authService';

export const getUserList = async () => {
    try {
      const token = AuthService.getCurrentUser()?.access_token;
      if (token) {
        const response = await instance.get('/users/', {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        console.log(response.data);
        return response.data;
      }
      throw new Error('No access token available');
    } catch (error) {
      throw error;
    }
  };

export const getUserDetail = (id) => instance.get(`/users/${id}/`);
export const uploadProfilePic = (data) => instance.post(`/users/upload_profile_pic/`, data);
export const acceptUser = (id) => instance.post(`/users/${id}/accept/`);
export const declineUser = (id) => instance.post(`/users/${id}/decline/`);
export const getUserProfile = (id) => instance.get(`/users/${id}/profile/`);
export const getReceivedFriendRequests = (id) => instance.get(`/users/${id}/received_friend_requests/`);
export const getSentFriendRequests = (id) => instance.get(`/users/${id}/sent_friend_requests/`);
export const getSocialMediaAccounts = (id) => instance.get(`/users/${id}/social_media_accounts/`);
