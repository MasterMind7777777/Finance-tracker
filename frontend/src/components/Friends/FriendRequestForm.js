
import React, { useState } from 'react';
import authService from '../../services/authService';

const FriendRequestForm = () => {
  const [userId, setUserId] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();

    // You may need to create this function in your services
    // depending on your existing codebase
    await authService.sendFriendRequest(userId);

    setUserId('');
  };

  return (
    <form onSubmit={handleSubmit}>
      <label>
        User ID:
        <input type="text" value={userId} onChange={(e) => setUserId(e.target.value)} />
      </label>
      <input type="submit" value="Send Friend Request" />
    </form>
  );
};

export default FriendRequestForm;
