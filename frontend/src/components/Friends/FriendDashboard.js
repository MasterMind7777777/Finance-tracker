import React, { useContext } from 'react';
import FriendList from './FriendList';
import FriendRequestList from './FriendRequestList';
import authService from '../../services/authService';

const FriendDashboard = () => {
  const { user } = authService.getCurrentUserId
  console.log(user);
  return (
    <div>
      <h2>{user.username}'s Profile</h2>
      <FriendList user={user} />
      <FriendRequestList user={user} />
    </div>
  )
}

export default FriendDashboard;
