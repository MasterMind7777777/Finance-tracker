import React from 'react';
import { acceptUser, declineUser } from '../../api/users';

const FriendRequest = ({request, user, onRespond}) => {
  const handleAccept = async () => {
    await acceptUser(request.from_user);
    onRespond();
  }

  const handleDecline = async () => {
    await declineUser(request.from_user);
    onRespond();
  }

  return (
    <div>
      <p>{request.from_user}'s friend request</p>
      <button onClick={handleAccept}>Accept</button>
      <button onClick={handleDecline}>Decline</button>
    </div>
  )
}
export default FriendRequest;
