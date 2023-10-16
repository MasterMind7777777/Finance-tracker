import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import {
  getReceivedFriendRequests,
  getSentFriendRequests,
} from '../../api/users';
import FriendRequest from './FriendRequest';
import { logMessage } from '../../api/loging'; // Import logMessage function

const FriendRequestList = ({ user }) => {
  const [receivedRequests, setReceivedRequests] = useState([]);
  const [sentRequests, setSentRequests] = useState([]);

  const fetchRequests = async () => {
    try {
      const received = await getReceivedFriendRequests(user.id);
      const sent = await getSentFriendRequests(user.id);

      // Filter out completed requests
      setReceivedRequests(received.filter((request) => !request.accepted));
      setSentRequests(sent.filter((request) => !request.accepted));

      logMessage(
        'info',
        `Fetched friend requests for User ID: ${user.id}`,
        'FriendRequestList',
      );
    } catch (error) {
      logMessage(
        'error',
        `Failed to fetch friend requests for User ID: ${user.id}. Error: ${error.message}`,
        'FriendRequestList',
      );
    }
  };

  useEffect(() => {
    fetchRequests();
  }, []);

  const handleRespond = () => {
    fetchRequests();
    logMessage(
      'info',
      `Updated friend requests after user action for User ID: ${user.id}`,
      'FriendRequestList',
    );
  };

  return (
    <div>
      <h3>Received Friend Requests</h3>
      {receivedRequests.map((request) => (
        <FriendRequest
          key={request.id}
          request={request}
          onRespond={handleRespond}
        />
      ))}
      <h3>Sent Friend Requests</h3>
      {sentRequests.map((request) => (
        <FriendRequest
          key={request.id}
          request={request}
          onRespond={handleRespond}
        />
      ))}
    </div>
  );
};

FriendRequestList.propTypes = {
  user: PropTypes.shape({
    id: PropTypes.number.isRequired,
  }).isRequired,
};

export default FriendRequestList;
