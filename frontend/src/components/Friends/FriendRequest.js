import React from 'react';
import PropTypes from 'prop-types';
import { acceptUser, declineUser } from '../../api/users';

const FriendRequest = ({ request, user, onRespond }) => {
  const handleAccept = async () => {
    await acceptUser(request.from_user);
    onRespond();
  };

  const handleDecline = async () => {
    await declineUser(request.from_user);
    onRespond();
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
