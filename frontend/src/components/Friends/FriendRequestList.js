import React, { useEffect, useState } from 'react';
import { getReceivedFriendRequests, getSentFriendRequests } from '../../api/users';
import FriendRequest from './FriendRequest';

const FriendRequestList = ({user}) => {
  const [receivedRequests, setReceivedRequests] = useState([]);
  const [sentRequests, setSentRequests] = useState([]);

  const fetchRequests = async () => {
    const received = await getReceivedFriendRequests(user.id);
    const sent = await getSentFriendRequests(user.id);
    // Filter out completed requests
    setReceivedRequests(received.filter(request => !request.accepted));
    setSentRequests(sent.filter(request => !request.accepted));
  }

  useEffect(() => {
    fetchRequests();
  }, []);

  const handleRespond = () => {
    fetchRequests();
  }

  return (
    <div>
      <h3>Received Friend Requests</h3>
      {receivedRequests.map(request => 
        <FriendRequest key={request.id} request={request} onRespond={handleRespond} />
      )}
      <h3>Sent Friend Requests</h3>
      {sentRequests.map(request => 
        <FriendRequest key={request.id} request={request} onRespond={handleRespond} />
      )}
    </div>
  )
}
export default FriendRequestList;
