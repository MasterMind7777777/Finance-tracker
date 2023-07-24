import React, { useEffect, useState } from 'react';
import { getFriendsList } from '../../api/users';

const FriendList = ({user}) => {
  const [friends, setFriends] = useState([]);

  const fetchFriends = async () => {
    const result = await getFriendsList(user);
    // Filter out only the accepted requests where the current user is the 'to_user'
    const friends = result.data.filter(req => req.accepted && req.to_user === user.id).map(req => req.from_user);
    setFriends(friends);
  }

  useEffect(() => {
    fetchFriends();
  }, []);

  return (
    <div>
      <h3>Friend List</h3>
      <ul>
        {friends.map(friend => <li key={friend.id}>{friend.username}</li>)}
      </ul>
    </div>
  )
}
export default FriendList;
