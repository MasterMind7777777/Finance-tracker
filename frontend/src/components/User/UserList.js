import React, { useEffect, useState } from 'react';
import { getUserList } from '../../api/users';
import AuthService from '../../services/authService';

const UserList = () => {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    const token = AuthService.getCurrentUser()?.access_token;
    if (token) {
      getUserList(token)
        .then(data => setUsers(data))
        .catch(err => console.error(err));
    }
  }, []);

  return (
    <div>
      <h1>User List</h1>
      {users.map(user => (
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