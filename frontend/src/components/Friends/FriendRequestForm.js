import React, { useState } from 'react';
import { sendFriendRequest } from '../../api/users';
import { logMessage } from '../../api/loging'; // Import logMessage function

const FriendRequestForm = () => {
  const [userId, setUserId] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      await sendFriendRequest(userId);
      logMessage(
        'info',
        `Sent friend request to User ID: ${userId}`,
        'FriendRequestForm',
      );
      setUserId('');
    } catch (error) {
      logMessage(
        'error',
        `Failed to send friend request to User ID: ${userId}. Error: ${error.message}`,
        'FriendRequestForm',
      );
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <label>
        User ID:
        <input
          type="text"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
        />
      </label>
      <input type="submit" value="Send Friend Request" />
    </form>
  );
};

export default FriendRequestForm;
