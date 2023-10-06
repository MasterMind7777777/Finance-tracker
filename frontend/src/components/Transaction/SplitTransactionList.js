import React, { useState, useEffect } from 'react';
import {
  getSplitTransactions,
  acceptTransactionSplit,
  declineTransactionSplit,
} from '../../api/transaction';

const SplitTransactionList = () => {
  const [splitTransactions, setSplitTransactions] = useState([]);

  const fetchSplitTransactions = async () => {
    try {
      const response = await getSplitTransactions();
      console.log(response);
      setSplitTransactions(response);
    } catch (error) {
      console.error('Error fetching split transactions:', error);
    }
  };

  useEffect(() => {
    fetchSplitTransactions(); // Call fetchSplitTransactions when the component mounts
  }, []); // Empty dependency array means this useEffect runs once, similar to componentDidMount

  const handleAccept = async (id) => {
    await acceptTransactionSplit(id);
    fetchSplitTransactions(); // refresh the list
  };

  const handleDecline = async (id) => {
    await declineTransactionSplit(id);
    fetchSplitTransactions(); // refresh the list
  };

  return (
    <ul>
      {splitTransactions.map((split) => (
        <li key={split.id}>
          {split.transaction_title} - {split.status}
          {split.status === 'pending' && (
            <>
              <button onClick={() => handleAccept(split.id)}>Accept</button>
              <button onClick={() => handleDecline(split.id)}>Decline</button>
            </>
          )}
        </li>
      ))}
    </ul>
  );
};

export default SplitTransactionList;
