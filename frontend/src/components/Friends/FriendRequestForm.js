import React, { useState } from 'react';
import { sendFriendRequest } from '../../api/users';

const FriendRequestForm = () => {
  const [userId, setUserId] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();

    await sendFriendRequest(userId);

    setUserId('');
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
