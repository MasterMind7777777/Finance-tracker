import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { getFriendsList } from '../../api/users';
import { logMessage } from '../../api/loging'; // Import logMessage function

const FriendList = ({ user }) => {
  const [friends, setFriends] = useState([]);

  const fetchFriends = async () => {
    try {
      const result = await getFriendsList(user.id);
      setFriends(result);
      logMessage(
        'info',
        `Successfully fetched friends for user ID ${user.id}`,
        'FriendList',
      );
    } catch (error) {
      logMessage(
        'error',
        `Error fetching friends for user ID ${user.id}: ${error.message}`,
        'FriendList',
      );
    }
  };

  useEffect(() => {
    logMessage('info', 'FriendList component mounted', 'FriendList');
    if (user) {
      fetchFriends();
    } else {
      logMessage(
        'warn',
        'User not defined in FriendList component',
        'FriendList',
      );
    }
  }, [user]);

  return (
    <div>
      <h3>Friend List</h3>
      <ul>
        {friends.map((friend) => (
          <li key={friend.id}>{friend.username}</li>
        ))}
      </ul>
    </div>
  );
};

FriendList.propTypes = {
  user: PropTypes.shape({
    id: PropTypes.number.isRequired,
  }).isRequired,
};

export default FriendList;
