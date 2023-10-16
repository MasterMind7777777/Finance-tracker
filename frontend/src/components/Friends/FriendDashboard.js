import React, { useEffect } from 'react'; // Import useEffect
import FriendList from './FriendList';
import FriendRequestList from './FriendRequestList';
import FriendRequestForm from './FriendRequestForm';
import authService from '../../services/authService';
import { logMessage } from '../../api/loging'; // Import logMessage function

const FriendDashboard = () => {
  const user = authService.getCurrentUser().user;

  // Log when the component mounts and possibly when user data changes
  useEffect(() => {
    logMessage('info', 'FriendDashboard component mounted', 'FriendDashboard');
    if (user) {
      logMessage('info', `Current user: ${user.username}`, 'FriendDashboard');
    } else {
      logMessage('error', 'User data is unavailable', 'FriendDashboard');
    }
  }, [user]);

  return (
    <div>
      <h2>{user.username}&apos;s Profile</h2>
      <FriendList user={user} />
      <FriendRequestList user={user} />
      <FriendRequestForm />
    </div>
  );
};

export default FriendDashboard;
