import { authenticatedRequest } from './index.js';

export const getUserList = () => authenticatedRequest('get', '/users/');
export const getUserDetail = (id) => authenticatedRequest('get', `/users/${id}/`);
export const uploadProfilePic = (data) => authenticatedRequest('post', `/users/upload_profile_pic/`, data);
export const acceptUser = (id) => authenticatedRequest('post', `/users/${id}/accept/`);
export const declineUser = (id) => authenticatedRequest('post', `/users/${id}/decline/`);
export const getUserProfile = (id) => authenticatedRequest('get', `/users/${id}/profile/`);
export const getReceivedFriendRequests = (id) => authenticatedRequest('get', `/users/${id}/received_friend_requests/`);
export const getSentFriendRequests = (id) => authenticatedRequest('get', `/users/${id}/sent_friend_requests/`);
export const getSocialMediaAccounts = (id) => authenticatedRequest('get', `/users/${id}/social_media_accounts/`);
