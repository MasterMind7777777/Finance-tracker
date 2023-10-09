import React from 'react';
import FriendList from './FriendList';
import FriendRequestList from './FriendRequestList';
import FriendRequestForm from './FriendRequestForm';
import authService from '../../services/authService';

const FriendDashboard = () => {
  const user = authService.getCurrentUser().user;
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
