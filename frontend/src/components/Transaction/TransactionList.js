import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getTransactionList } from '../../api/transaction';
import AuthService from '../../services/authService';

const TransactionList = () => {
  const [transactions, setTransactions] = useState([]);

  useEffect(() => {
    const token = AuthService.getCurrentUser()?.access_token;
    if (token) {
      getTransactionList(token)
        .then(data => setTransactions(data))
        .catch(err => console.error(err));
    }
  }, []);

  return (
    <div>
      <h1>Transaction List</h1>
      {transactions.map(transaction => (
        <div key={transaction.id}>
          <h2>{transaction.title}</h2>
          <p>{transaction.amount}</p>
          <p>{transaction.date}</p>
          <p>{transaction.category}</p>
          <Link to={`/transactions/${transaction.id}`}>View Details</Link>
        </div>
      ))}
    </div>
  );
};

export default TransactionList;
