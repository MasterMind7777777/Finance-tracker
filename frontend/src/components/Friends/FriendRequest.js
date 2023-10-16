import React from 'react';
import PropTypes from 'prop-types';
import { acceptUser, declineUser } from '../../api/users';
import { logMessage } from '../../api/loging'; // Import logMessage function

const FriendRequest = ({ request, user, onRespond }) => {
  const handleAccept = async () => {
    try {
      await acceptUser(request.from_user);
      logMessage(
        'info',
        `Friend request from ${request.from_user} accepted by ${user}`,
        'FriendRequest',
      );
      onRespond();
    } catch (error) {
      logMessage(
        'error',
        `Error accepting friend request from ${request.from_user}: ${error.message}`,
        'FriendRequest',
      );
    }
  };

  const handleDecline = async () => {
    try {
      await declineUser(request.from_user);
      logMessage(
        'info',
        `Friend request from ${request.from_user} declined by ${user}`,
        'FriendRequest',
      );
      onRespond();
    } catch (error) {
      logMessage(
        'error',
        `Error declining friend request from ${request.from_user}: ${error.message}`,
        'FriendRequest',
      );
    }
  };

  return (
    <div>
      <p>{`${request.from_user}'s friend request`}</p>{' '}
      {/* Escape the character */}
      <button onClick={handleAccept}>Accept</button>
      <button onClick={handleDecline}>Decline</button>
    </div>
  );
};

// Define the prop types
FriendRequest.propTypes = {
  request: PropTypes.shape({
    from_user: PropTypes.string.isRequired,
  }).isRequired,
  user: PropTypes.string.isRequired,
  onRespond: PropTypes.func.isRequired,
};

export default FriendRequest;
