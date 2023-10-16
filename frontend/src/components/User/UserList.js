import React, { useEffect, useState } from 'react';
import { getUserList } from '../../api/users';
import AuthService from '../../services/authService';
import { logMessage } from '../../api/loging';

const UserList = () => {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    const token = AuthService.getCurrentUser()?.access_token;
    if (token) {
      getUserList(token)
        .then((data) => {
          setUsers(data);
          logMessage('info', 'User list fetched successfully.', 'UserList'); // Log successful data fetching
        })
        .catch((err) => {
          console.error(err);
          logMessage('error', `Error fetching user list: ${err}`, 'UserList'); // Log the error
        });
    } else {
      logMessage(
        'warn',
        'Access token not found. Fetching user list aborted.',
        'UserList',
      ); // Log the absence of a token
    }
  }, []);

  return (
    <div>
      <h1>User List</h1>
      {users.map((user) => (
        <div key={user.id}>
          <h2>{user.username}</h2>
          <p>{user.date_of_birth}</p>
          <p>{user.phone_number}</p>
          <p>{user.userprofile}</p>
        </div>
      ))}
    </div>
  );
};

export default UserList;
